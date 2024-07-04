### Развертывание 

```bash
docker-compose up -d --build
```

### Первый запуск

1. Запустите PostgreSQL и войдите в консоль:

```bash
docker exec -it postgres psql -U postgres -p 5432
```

2. Вставте записи в таблицу:

```bash
INSERT INTO order_types (id, name) VALUES (1, 'Clothing'), (2, 'Electronics'), (3, 'Miscellaneous');
```
