FROM ruby:3.1.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git \
       curl \
       libssl-dev \
       libreadline-dev \
       zlib1g-dev \
       autoconf \
       bison \
       build-essential \
       libyaml-dev \
       libreadline-dev \
       libncurses5-dev \
       libffi-dev \
       libgdbm-dev \
       nodejs \
       vim \
       nano \
       apache2-utils

WORKDIR /var/app/

COPY . /var/app/

WORKDIR /var/app/learn-rails

# by enabling this, the special/experimental liboboe will be installed for benchmarking
ARG SPECIAL_LIBOBOE
ARG OBOE_ENV
ARG BUNDLE_RUBYGEMS__PKG__GITHUB__COM

RUN bundle install

RUN gem list | grep solarwinds_apm | awk -F'[()]' '{print $2}' > /solarwinds_version.txt

RUN version=$(cat /solarwinds_version.txt) && \
    cp /var/app/otel_config.rb /usr/local/bundle/gems/solarwinds_apm-${version}/lib/solarwinds_apm/

# otel_config.rb branch off either OTLP_MODE_ON true or false
# COPY otel_config.rb /usr/local/bundle/gems/solarwinds_apm-6.1.0/lib/solarwinds_apm/
# COPY otel_config.rb /usr/local/bundle/gems/solarwinds_apm-6.1.0/lib/solarwinds_apm/

EXPOSE 8002

CMD ["rails", "server", "-b", "0.0.0.0", "-p", "8002"]
# CMD ["tail", "-f", "/dev/null"]
# rails server -b 0.0.0.0 -p 8002
