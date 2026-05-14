# doc-chat
RAG-система для работы со своей коллекцией текстовых документов локально с применением локальной LLM.


Текущий статус: в разработке.

## Запуск elasticsearch

Для linux:
```
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0

```


Остановка контейтера:

```
docker stop elasticsearch
```

Удаление контейтера:
```
docker rm elasticsearch
```