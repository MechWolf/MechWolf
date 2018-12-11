cat apparatus_example.yaml | yaml2json > apparatus_example.json
cat mechwolf.schema.yaml | yaml2json >  mechwolf.schema.json
jsonschema mechwolf.schema.json -i apparatus_example.json
rm -rf mechwolf.schema.json apparatus_example.json
