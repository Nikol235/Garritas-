# Build from repository root, using this Dockerfile with -f.
FROM maven:3.9.16-eclipse-temurin-21 AS build
WORKDIR /build
COPY . .
ARG MODULE=infra/garritas-eureka
RUN test -n "$MODULE" && mvn -B -pl "$MODULE" -am package -DskipTests && cp "$MODULE"/target/*-SNAPSHOT.jar /app.jar
FROM eclipse-temurin:21-jre
WORKDIR /app
RUN mkdir -p /app/logs && chown -R 10001:10001 /app
COPY --from=build --chown=10001:10001 /app.jar /app/app.jar
COPY --from=build --chown=10001:10001 /build/infra/garritas-config/config-repo /config-repo
USER 10001
ENTRYPOINT ["java","-XX:MaxRAMPercentage=70","-jar","/app/app.jar"]
