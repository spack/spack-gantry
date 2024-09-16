# Testing CI Generation Locally

If you want to test Gantry's prediction functionality on your local machine rather than needing an entire K8s cluster, it can be done in a few commands:

```bash
cd gantry/dev/generate_local
spack env activate .
mkdir mirror && spack mirror create -d mirror zlib
# add local mirror to spack.yaml
spack mirror add local_filesystem file://$PWD/mirror
spack ci generate --output-file pipeline.yaml --artifacts-root tmp
```

As you can see in `spack.yaml`, we're using `zlib` as an example spec to predict usage. This can be changed if you'd prefer to experiment with a heavier build. 

The default Gantry endpoint is `localhost:8080`, so be sure to start your server and point `DB_FILE` to a database with sufficient training data. If you're on a Mac, the AWS data likely doesn't have any samples with `apple-clang` as a compiler, so you might have to update the database with `compiler_name='apple-clang'` (and the corresponding version) to get predictions.

Once the generate process is done, you can see in `pipeline.yaml` that `KUBERNETES*` variables were set.
