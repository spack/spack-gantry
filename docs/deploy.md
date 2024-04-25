# Deploy

Gantry is distributed via containers. You can build an image using your favorite container engine:

```bash
podman build -t gantry .
```

In order for the application to run, you'll need to supply two things to the image: environment variables and a database file.

When running locally, you can get by with supplying an env file and volume, like so:

```bash
podman run -it -p 8080:8080 --env-file .env -v LOCAL_DB_PATH:DB_FILE gantry
```

Where `LOCAL_DB_PATH` is the absolute path to the database file on your local system. `DB_FILE` is where you would like the application to access the database. Make sure this lines up with your environment.

When running Gantry within Kubernetes, you could use [persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/). The only requirement is that the database should exist outside the container for backup and persistence purposes.

## Environment

The following variables should be exposed to the container. Those **bolded** are required and do not have defaults set in the application.

- **`PROMETHEUS_URL`** - should end in `/api/v1`
- `PROMETHEUS_COOKIE` - only needed when Prometheus requires authentication
- **`GITLAB_URL`** - should end in the endpoint for the Spack project API: `/api/v4/projects/2`
- **`GITLAB_API_TOKEN`** - this token should have API read access
- **`GITLAB_WEBHOOK_TOKEN`** - coordinate this value with the collection webhook
- **`DB_FILE`** - path where the application can access the SQLite file
