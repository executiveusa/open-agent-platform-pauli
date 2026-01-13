FROM mcr.microsoft.com/playwright:v1.52.0-jammy

RUN apt-get update && apt-get install -y x11vnc xvfb websockify novnc && rm -rf /var/lib/apt/lists/*

WORKDIR /runner
COPY start.sh /runner/start.sh
RUN chmod +x /runner/start.sh

EXPOSE 5900 6080

CMD ["/runner/start.sh"]
