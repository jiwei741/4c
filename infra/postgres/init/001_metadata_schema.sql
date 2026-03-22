CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS study_areas (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    north DOUBLE PRECISION NOT NULL,
    west DOUBLE PRECISION NOT NULL,
    south DOUBLE PRECISION NOT NULL,
    east DOUBLE PRECISION NOT NULL,
    aoi_geom geometry(Polygon, 4326) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
    id BIGSERIAL PRIMARY KEY,
    source_type TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    request_payload JSONB,
    status TEXT NOT NULL DEFAULT 'pending',
    log_path TEXT,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS raw_assets (
    id BIGSERIAL PRIMARY KEY,
    source_type TEXT NOT NULL,
    dataset_name TEXT NOT NULL,
    external_id TEXT,
    asset_name TEXT NOT NULL,
    asset_time TIMESTAMPTZ,
    local_path TEXT,
    remote_uri TEXT,
    format TEXT,
    size_bytes BIGINT,
    checksum TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_assets_source_dataset_asset
    ON raw_assets (source_type, dataset_name, asset_name);

CREATE TABLE IF NOT EXISTS sentinel2_catalog (
    id BIGSERIAL PRIMARY KEY,
    study_area_id BIGINT NOT NULL REFERENCES study_areas(id),
    product_id TEXT NOT NULL UNIQUE,
    tile_id TEXT NOT NULL,
    collection TEXT NOT NULL,
    acquisition_time TIMESTAMPTZ NOT NULL,
    platform TEXT,
    cloud_cover DOUBLE PRECISION,
    epsg INTEGER,
    s3_href TEXT,
    self_href TEXT,
    footprint_geom geometry(MultiPolygon, 4326),
    raw_asset_id BIGINT REFERENCES raw_assets(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sentinel2_catalog_area_time
    ON sentinel2_catalog (study_area_id, acquisition_time DESC);

CREATE INDEX IF NOT EXISTS idx_sentinel2_catalog_tile
    ON sentinel2_catalog (tile_id);

CREATE TABLE IF NOT EXISTS sentinel2_download_plan (
    id BIGSERIAL PRIMARY KEY,
    study_area_id BIGINT NOT NULL REFERENCES study_areas(id),
    priority INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    tile_id TEXT NOT NULL,
    planned_filename TEXT NOT NULL,
    overlap_ratio DOUBLE PRECISION,
    cloud_cover DOUBLE PRECISION,
    status TEXT NOT NULL DEFAULT 'planned',
    raw_asset_id BIGINT REFERENCES raw_assets(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_sentinel2_download_plan_area_product
    ON sentinel2_download_plan (study_area_id, product_id);

CREATE TABLE IF NOT EXISTS era5_requests (
    id BIGSERIAL PRIMARY KEY,
    study_area_id BIGINT NOT NULL REFERENCES study_areas(id),
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    variables JSONB NOT NULL,
    request_id TEXT,
    status TEXT NOT NULL DEFAULT 'planned',
    output_path TEXT,
    request_payload JSONB,
    raw_asset_id BIGINT REFERENCES raw_assets(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_era5_requests_area_year_month
    ON era5_requests (study_area_id, year, month);

CREATE TABLE IF NOT EXISTS noaa_files (
    id BIGSERIAL PRIMARY KEY,
    dataset_name TEXT NOT NULL UNIQUE,
    source_url TEXT NOT NULL,
    local_path TEXT,
    raw_asset_id BIGINT REFERENCES raw_assets(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
