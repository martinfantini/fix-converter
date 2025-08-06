# fix-converter-gen

The idea is generate a python program, which generate the basis classes for fix stream converter.

* inspired by https://github.com/ksergey/sbe-code-gen/

## Fix definition

The possible example of fix definition are in the ```resources``` folder.

### Observation:
In the case of the t=group generation, if there is a group inside another group (nested group), the correct definition is to have two components like:

```
component_nested_group:
    - fields
    - group_definition
        - fields
        - fields
component_group:
    - fields
    - component_nested_group
    - fields
```

## Run generator

To run the fix-generator:

```bash
python3.13 -m app --schema resources/FIXLF44_Cash.xml --generator cpp --destination result
```

# TODO

- [ ] tests
- [x] ci integration on push and pull
- [ ] ci integration advance
- [ ] cmake integration
- [ ] rust support
- [ ] (cppng) from/to json serialization
