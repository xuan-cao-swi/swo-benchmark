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
end

require 'solarwinds_apm'

SolarWindsAPM::OpenTelemetry::OTLPProcessor.prepend(OverWriteMetrics) if defined? (::SolarWindsAPM::OpenTelemetry)

SecureHeaders::Configuration.default if defined?(SecureHeaders)

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
