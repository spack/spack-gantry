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

When running Gantry within Kubernetes, you could use [persistent volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/). The only requirement is that a copy of the database should exist outside the container for backup and persistence purposes.

## Container

When modifying the Dockerfile, keep in mind that the Python version in the container depends on the distribution (Debian). Google's "[distroless](https://github.com/GoogleContainerTools/distroless)" containers, which we use as a base image, do not provide a mechanism to specify a Python version (major, minor, or patch). Therefore, check the [Debian documentation](https://wiki.debian.org/Python) to see which  version is included in the distro and verify that all tests pass before modifying the image.

## Environment

The following variables should be exposed to the container. Those **bolded** are required and do not have defaults set in the application.

- **`PROMETHEUS_URL`** - should end in `/api/v1`
- `PROMETHEUS_COOKIE` - only needed when Prometheus requires authentication
- **`GITLAB_URL`** - should end in the endpoint for the Spack project API: `/api/v4/projects/2`
- **`GITLAB_API_TOKEN`** - this token should have API read access
- **`GITLAB_WEBHOOK_TOKEN`** - coordinate this value with the collection webhook
- **`DB_FILE`** - path where the application can access the SQLite file

## Kubernetes

Gantry can be deployed in a Kubernetes cluster. For an example of how we do this within Spack's web infrastructure, see [this folder](https://github.com/spack/spack-infrastructure/tree/main/k8s/production/spack/gantry-spack-io) containing configuration files and instructions.

While most details are better suited to be documented with the cluster, there are some considerations that are general to any Gantry deployment.

### Database

We have made an architectural decision to depend on SQLite as the database engine. Before you deploy Gantry into a cluster, you should ensure that the file will be backed up on a regular basis, in the case that unexpected circumstances corrupt your data. This can be achieved using [Litestream](https://litestream.io), which will continuously replicate the database with the storage provider of your choice. See the cluster configuration linked above for details.

When first deployed, the application will create `$DB_FILE` if it doesn't already exist. It will not create directories in the path.

**Migrations**

Changes to the database schema are stored in the `migrations/` directory. Follow the naming convention `000_name.sql` and place new items in the `migrations` list inside the `gantry/__main__.py:apply_migrations` function.
