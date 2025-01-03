
meter = OpenTelemetry.meter_provider.meter("benchmark-meter")
Rails.application.config.cpu_counter = meter.create_counter('xuan.ruby.service.cpu', unit: 'smidgen', description: 'a small amount of something')
Rails.application.config.memory_counter = meter.create_counter('xuan.ruby.service.memory', unit: 'smidgen', description: 'a small amount of something')
Rails.application.config.latency_histogram = meter.create_histogram('xuan.ruby.service.response.time', unit: 'smidgen', description: 'a small amount of something')
