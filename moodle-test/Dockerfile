FROM php:8.2-apache

RUN apt-get update && apt-get install -y \
    libpng-dev libjpeg-dev libfreetype6-dev libzip-dev libicu-dev libxml2-dev \
    git unzip wget \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd zip intl mysqli opcache soap exif

RUN echo "max_input_vars = 5000" > /usr/local/etc/php/conf.d/moodle.ini

RUN git clone -b MOODLE_405_STABLE --depth 1 https://github.com/moodle/moodle.git /var/www/html \
    && mkdir -p /var/www/moodledata \
    && chown -R www-data:www-data /var/www/html /var/www/moodledata