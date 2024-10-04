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

RUN bundle install

COPY otel_config.rb /usr/local/bundle/gems/solarwinds_apm-6.1.0/lib/solarwinds_apm/

EXPOSE 8002

CMD ["rails", "server", "-b", "0.0.0.0", "-p", "8002"]

# rails server -b 0.0.0.0 -p 8002
# CMD ["tail", "-f", "/dev/null"]