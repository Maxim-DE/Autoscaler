



# Prometheus
http://45.84.224.156:9000/query

# Grafana
http://45.84.224.156:3000/d/bc96dd35-dc52-4ae0-a77e-01c9e04e00cb/y0nei-s-cadvisor-dashboard?var-interval=5m&orgId=1&from=now-5m&to=now&timezone=browser&var-instance=Worker1&var-job=cadvisor&var-container=$__all&refresh=5s

# Приложение my-app
http://155.212.223.84/

# Cadvisor
http://45.84.224.156:8080/


# Пример запросов Prometheus на CPU приложения my-app на всех воркерах
rate(container_cpu_usage_seconds_total{
  node_name=~"Worker.*",
  container_label_com_docker_stack_namespace="my-app",
  image!=""
}[1m]) * 100

## По cgroup (система, docker, systemd)
sum by (id) (
  rate(container_cpu_usage_seconds_total{
    node_name="Worker2"
  }[1m])
) * 100

