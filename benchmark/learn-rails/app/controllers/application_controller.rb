class ApplicationController < ActionController::Base
  protect_from_forgery with: :exception
  before_action :start_stats
  after_action :log_stats

  private

  def start_stats
    @start_time = Time.now
    # @start_memory = memory_usage
    # @start_cpu = cpu_usage
  end

  def log_stats
    end_time = Time.now
    # end_memory = memory_usage
    # end_cpu = cpu_usage

    time_taken = end_time - @start_time
    # memory_used = end_memory - @start_memory
    # cpu_used = end_cpu - @start_cpu

    # Log the stats (you can log, save, or send them elsewhere)
    Rails.logger.info "Request took #{time_taken.round(4)}s"
    # Rails.logger.info "Memory used: #{memory_used.round(2)} MB"
    # Rails.logger.info "CPU used: #{cpu_used.round(4)}s"

    agent_type = ENV['AGENT_TYPE']
    # Rails.application.config.cpu_counter.add(cpu_used, attributes: { 'xuan-test' => agent_type })
    # Rails.application.config.memory_counter.add(memory_used, attributes: { 'xuan-test' => agent_type })
    Rails.application.config.latency_histogram.record(time_taken, attributes: {'xuan-test' => agent_type })

    puts "::OpenTelemetry.meter_provider.metric_readers.size: #{::OpenTelemetry.meter_provider.metric_readers.size}"

    if ::OpenTelemetry.meter_provider.metric_readers.size == 1
      ::OpenTelemetry.meter_provider.metric_readers.first.pull
    elsif ::OpenTelemetry.meter_provider.metric_readers.size == 2
      ::OpenTelemetry.meter_provider.metric_readers[1].pull
    end
  end

  # Method to calculate current memory usage in MB
  def memory_usage
    `ps -o rss= -p #{Process.pid}`.to_i / 1024.0
  end

  # Method to calculate current CPU usage in seconds
  def cpu_usage
    `ps -o %cpu= -p #{Process.pid}`.to_f / 100.0
  end

  def log_request_duration
    request_duration = (Time.now - request.env['action_dispatch.request.start_time']) * 1000.0
    Rails.logger.info "Request duration: #{request_duration.round(2)}ms"
  end

  def cpu_time
    # Fetch CPU time and process stats from /proc
    stat = File.read("/proc/#{Process.pid}/stat").split

    # Extract values
    utime = stat[13].to_i # User mode time in clock ticks
    stime = stat[14].to_i # Kernel mode time in clock ticks
    clock_ticks_per_second = 100.0 # Typically 100 Hz, but check your system's value

    # Calculate CPU time
    cpu_time_seconds = (utime + stime) / clock_ticks_per_second
    puts "CPU Time: #{cpu_time_seconds.round(2)} seconds"

    start_time = stat[21].to_i / clock_ticks_per_second # Process start time
    uptime = File.read("/proc/uptime").split[0].to_f # System uptime in seconds

    elapsed_time = uptime - start_time
    cpu_usage_percentage = (cpu_time_seconds / elapsed_time) * 100
    puts "CPU Usage: #{cpu_usage_percentage.round(2)}%"
  end

  def monitor_cpu_usage
    # Start measuring time before the controller action
    start_time = Process.clock_gettime(Process::CLOCK_MONOTONIC)
    
    # Execute the controller action
    yield

    # Measure CPU time after the action has executed
    end_time = Process.clock_gettime(Process::CLOCK_MONOTONIC)
    cpu_time = end_time - start_time

    # Log CPU time in seconds (you can multiply by 1000 for milliseconds)
  end
end
