require_relative 'boot'

require 'rails/all'

# Require the gems listed in Gemfile, including any gems
# you've limited to :test, :development, or :production.
Bundler.require(*Rails.groups)

module LearnRailsApp
  module JavaCollector
    def sanitize_collector_uri(uri)
      if ENV['SW_APM_COLLECTOR']
        ENV['SW_APM_COLLECTOR']
      else
        super(uri)
      end
    end
  end
end

if ENV['SW_APM_COLLECTOR'] =~ /java-collector:\d+/ || ENV['SW_APM_COLLECTOR'] =~ /java-collector-2:\d+/
  require 'solarwinds_apm/oboe_init_options'
  SolarWindsAPM::OboeInitOptions.prepend(LearnRailsApp::JavaCollector) if defined?(SolarWindsAPM::OboeInitOptions)
end

module OverWriteMetrics
  def record_sampling_metrics
    @metrics[:tracecount].add(rand(1..10))
    @metrics[:samplecount].add(rand(1..10))
    @metrics[:request_count].add(rand(1..10))
    @metrics[:toex_count].add(rand(1..10))
    @metrics[:through_count].add(rand(1..10))
    @metrics[:tt_count].add(rand(1..10))
  end

  def on_finish(span)
    SolarWindsAPM.logger.debug { "[#{self.class}/#{__method__}] processor on_finish span: #{span.to_span_data.inspect}" }

    # return if span is non-entry span
    return if non_entry_span(span: span)

    record_request_metrics(span)
    record_sampling_metrics

    ::OpenTelemetry.meter_provider.metric_readers.first.pull # this ensures only otlp processor related metrics get pull
    SolarWindsAPM.logger.debug { "[#{self.class}/#{__method__}] processor on_finish succeed" }
  rescue StandardError => e
    SolarWindsAPM.logger.info { "[#{self.class}/#{__method__}] error processing span on_finish: #{e.message}" }
  end
end

module OverWriteMetricsExporter
  def number_data_point(ndp)
    args = {
      attributes: ndp.attributes.map { |k, v| as_otlp_key_value(k, v) },
      start_time_unix_nano: ndp.start_time_unix_nano,
      time_unix_nano: ndp.time_unix_nano,
      exemplars: ndp.exemplars # exemplars not implemented yet from metrics sdk
    }

    if ndp.value.is_a?(Float)
      args[:as_double] = ndp.value
    else
      args[:as_int] = ndp.value
    end

    Opentelemetry::Proto::Metrics::V1::NumberDataPoint.new(**args)
  end
end

require 'solarwinds_apm'

SolarWindsAPM::OpenTelemetry::OTLPProcessor.prepend(OverWriteMetrics) if defined? (::SolarWindsAPM::OpenTelemetry)
OpenTelemetry::Exporter::OTLP::Metrics::MetricsExporter.prepend(OverWriteMetricsExporter) if defined? (::OpenTelemetry::Exporter::OTLP::Metrics::MetricsExporter)
SecureHeaders::Configuration.default if defined?(SecureHeaders)

# register metrics_exporter to meter_provider

if ENV['SW_APM_ENABLED'] == 'false'
  require 'opentelemetry/sdk'
  ::OpenTelemetry::SDK.configure { |c| c.use("OpenTelemetry::Instrumentation::HttpClient", {:enabled => false}) }
end

puts "ENV['OTEL_ENDPOINT']: #{ENV['OTEL_ENDPOINT']}"
puts "ENV['OTEL_HEADERS']: #{ENV['OTEL_HEADERS']}"
metrics_exporter = ::OpenTelemetry::Exporter::OTLP::Metrics::MetricsExporter.new(
  endpoint: ENV['OTEL_ENDPOINT'],
  headers: ENV['OTEL_HEADERS']
)
::OpenTelemetry.meter_provider.add_metric_reader(metrics_exporter)

module LearnRails
  class Application < Rails::Application
    # Initialize configuration defaults for originally generated Rails version.
    config.load_defaults 5.1

    # config.web_console.permissions = '172.17.0.1'

    # Settings in config/environments/* take precedence over those specified here.
    # Application configuration should go into files in config/initializers
    # -- all .rb files in that directory are automatically loaded.
  end
end
