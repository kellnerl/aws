#!/bin/bash
cp ./Dockerfile . 
DOCKER_BUILDKIT=0 docker build -t diskuze:latest .