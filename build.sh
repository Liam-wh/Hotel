#!/usr/bin/env bash

apt-get update

# Instala wkhtmltopdf y sus dependencias necesarias para renderizar correctamente
apt-get install -y \
  xfonts-75dpi \
  xfonts-base \
  wkhtmltopdf
