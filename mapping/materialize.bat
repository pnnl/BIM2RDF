ontop materialize ^
    --properties sqldb.properties ^
    -m mapping.obda ^
    -t Brick.ttl ^
    --disable-reasoning ^
    -f turtle ^
    -o mapping
    