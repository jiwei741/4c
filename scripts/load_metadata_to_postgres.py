import argparse
import json
from pathlib import Path
from typing import Any

import psycopg
from dotenv import dotenv_values


DEFAULT_ERA5_VARIABLES = [
    "10m_u_component_of_wind",
    "10m_v_component_of_wind",
    "2m_temperature",
    "total_precipitation",
]

NOAA_FILE_URLS = {
    "co2_mm_gl.csv": "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_gl.csv",
    "co2_annmean_gl.csv": "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_gl.csv",
    "co2_gr_gl.csv": "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_gr_gl.csv",
    "co2_trend_gl.csv": "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_trend_gl.csv",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load study area, Sentinel-2, ERA5 and NOAA metadata into PostgreSQL."
    )
    parser.add_argument("--area-name", default="nanjing")
    parser.add_argument("--north", type=float, default=32.7)
    parser.add_argument("--west", type=float, default=118.3)
    parser.add_argument("--south", type=float, default=31.2)
    parser.add_argument("--east", type=float, default=119.3)
    parser.add_argument(
        "--sentinel-catalog-json",
        default="data/raw/sentinel2/nanjing/catalog/sentinel2_nanjing_2025-01-01_to_2025-01-31.json",
    )
    parser.add_argument(
        "--sentinel-plan-json",
        default="data/raw/sentinel2/nanjing/catalog/sentinel2_download_plan_nanjing_2025-01-01_to_2025-01-31.json",
    )
    parser.add_argument(
        "--era5-output-path",
        default="data/raw/era5/nanjing/era5_nanjing_2025_01.nc",
    )
    parser.add_argument(
        "--era5-log-path",
        default="logs/era5_nanjing_2025_01.err.log",
    )
    parser.add_argument(
        "--noaa-dir",
        default="data/raw/noaa/co2",
    )
    return parser.parse_args()


def load_env(project_root: Path) -> dict[str, str]:
    env = dotenv_values(project_root / ".env")
    return {key: (value or "").strip() for key, value in env.items()}


def connect_db(env: dict[str, str]) -> psycopg.Connection:
    host = env.get("POSTGRES_HOST") or "127.0.0.1"
    port = env.get("POSTGRES_PORT") or "5432"
    dbname = env.get("POSTGRES_DB") or "spatio_eco"
    user = env.get("POSTGRES_USER") or "spatio_eco"
    password = env.get("POSTGRES_PASSWORD") or "spatio_eco_dev"
    return psycopg.connect(
        host=host,
        port=port,
        dbname=dbname,
        user=user,
        password=password,
    )


def ensure_study_area(
    conn: psycopg.Connection,
    *,
    name: str,
    north: float,
    west: float,
    south: float,
    east: float,
) -> int:
    wkt = (
        f"POLYGON(({west} {south},"
        f"{east} {south},"
        f"{east} {north},"
        f"{west} {north},"
        f"{west} {south}))"
    )
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO study_areas (name, north, west, south, east, aoi_geom)
            VALUES (%s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))
            ON CONFLICT (name) DO UPDATE
            SET north = EXCLUDED.north,
                west = EXCLUDED.west,
                south = EXCLUDED.south,
                east = EXCLUDED.east,
                aoi_geom = EXCLUDED.aoi_geom
            RETURNING id
            """,
            (name, north, west, south, east, wkt),
        )
        return cur.fetchone()[0]


def upsert_raw_asset(
    conn: psycopg.Connection,
    *,
    source_type: str,
    dataset_name: str,
    asset_name: str,
    external_id: str | None = None,
    asset_time: str | None = None,
    local_path: str | None = None,
    remote_uri: str | None = None,
    format_name: str | None = None,
    size_bytes: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO raw_assets (
                source_type, dataset_name, external_id, asset_name, asset_time,
                local_path, remote_uri, format, size_bytes, metadata
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
            ON CONFLICT (source_type, dataset_name, asset_name) DO UPDATE
            SET external_id = EXCLUDED.external_id,
                asset_time = EXCLUDED.asset_time,
                local_path = EXCLUDED.local_path,
                remote_uri = EXCLUDED.remote_uri,
                format = EXCLUDED.format,
                size_bytes = EXCLUDED.size_bytes,
                metadata = EXCLUDED.metadata
            RETURNING id
            """,
            (
                source_type,
                dataset_name,
                external_id,
                asset_name,
                asset_time,
                local_path,
                remote_uri,
                format_name,
                size_bytes,
                json.dumps(metadata or {}),
            ),
        )
        return cur.fetchone()[0]


def upsert_sentinel_catalog(
    conn: psycopg.Connection,
    *,
    study_area_id: int,
    catalog_path: Path,
) -> None:
    payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    for item in payload["products"]:
        download_candidate = Path("data/raw/sentinel2/downloads") / f"{item['id']}.zip"
        local_path = str(download_candidate.resolve()) if download_candidate.exists() else None

        raw_asset_id = upsert_raw_asset(
            conn,
            source_type="sentinel2",
            dataset_name="sentinel-2-l2a",
            external_id=item["id"],
            asset_name=item["id"],
            asset_time=item.get("datetime"),
            local_path=local_path,
            remote_uri=item.get("s3_href"),
            format_name="SAFE",
            size_bytes=download_candidate.stat().st_size if download_candidate.exists() else None,
            metadata=item,
        )

        geometry = item.get("geometry")
        bbox = item.get("bbox") or [None, None, None, None]

        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sentinel2_catalog (
                    study_area_id, product_id, tile_id, collection, acquisition_time,
                    platform, cloud_cover, epsg, s3_href, self_href, footprint_geom, raw_asset_id
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    CASE
                        WHEN %s IS NOT NULL THEN ST_Multi(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4326))
                        ELSE ST_Multi(ST_MakeEnvelope(%s, %s, %s, %s, 4326))
                    END,
                    %s
                )
                ON CONFLICT (product_id) DO UPDATE
                SET tile_id = EXCLUDED.tile_id,
                    collection = EXCLUDED.collection,
                    acquisition_time = EXCLUDED.acquisition_time,
                    platform = EXCLUDED.platform,
                    cloud_cover = EXCLUDED.cloud_cover,
                    epsg = EXCLUDED.epsg,
                    s3_href = EXCLUDED.s3_href,
                    self_href = EXCLUDED.self_href,
                    footprint_geom = EXCLUDED.footprint_geom,
                    raw_asset_id = EXCLUDED.raw_asset_id
                """,
                (
                    study_area_id,
                    item["id"],
                    item["id"].split("_")[5] if len(item["id"].split("_")) > 5 else "UNKNOWN",
                    item["collection"],
                    item.get("datetime"),
                    item.get("platform"),
                    item.get("cloud_cover"),
                    item.get("epsg"),
                    item.get("s3_href"),
                    item.get("self_href"),
                    json.dumps(geometry) if geometry else None,
                    json.dumps(geometry) if geometry else None,
                    bbox[0],
                    bbox[1],
                    bbox[2],
                    bbox[3],
                    raw_asset_id,
                ),
            )


def upsert_sentinel_plan(
    conn: psycopg.Connection,
    *,
    study_area_id: int,
    plan_path: Path,
) -> None:
    payload = json.loads(plan_path.read_text(encoding="utf-8"))
    with conn.cursor() as cur:
        for row in payload["downloads"]:
            cur.execute(
                """
                SELECT id FROM raw_assets
                WHERE source_type = 'sentinel2'
                  AND dataset_name = 'sentinel-2-l2a'
                  AND asset_name = %s
                """,
                (row["scene_id"],),
            )
            raw_asset = cur.fetchone()
            raw_asset_id = raw_asset[0] if raw_asset else None

            cur.execute(
                """
                INSERT INTO sentinel2_download_plan (
                    study_area_id, priority, product_id, tile_id, planned_filename,
                    overlap_ratio, cloud_cover, status, raw_asset_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'planned', %s)
                ON CONFLICT (study_area_id, product_id) DO UPDATE
                SET priority = EXCLUDED.priority,
                    tile_id = EXCLUDED.tile_id,
                    planned_filename = EXCLUDED.planned_filename,
                    overlap_ratio = EXCLUDED.overlap_ratio,
                    cloud_cover = EXCLUDED.cloud_cover,
                    raw_asset_id = EXCLUDED.raw_asset_id
                """,
                (
                    study_area_id,
                    row["priority"],
                    row["scene_id"],
                    row["tile_id"],
                    row["target_filename"],
                    row.get("overlap_ratio"),
                    row.get("cloud_cover"),
                    raw_asset_id,
                ),
            )


def parse_era5_request_id(log_path: Path) -> str | None:
    if not log_path.exists():
        return None
    for line in log_path.read_text(encoding="utf-8", errors="ignore").splitlines():
        marker = "Request ID is "
        if marker in line:
            return line.split(marker, 1)[1].strip()
    return None


def upsert_era5_request(
    conn: psycopg.Connection,
    *,
    study_area_id: int,
    output_path: Path,
    log_path: Path,
) -> None:
    request_id = parse_era5_request_id(log_path)
    raw_asset_id = upsert_raw_asset(
        conn,
        source_type="era5",
        dataset_name="reanalysis-era5-single-levels",
        external_id=request_id,
        asset_name=output_path.name,
        local_path=str(output_path.resolve()) if output_path.exists() else str(output_path),
        format_name="netcdf",
        size_bytes=output_path.stat().st_size if output_path.exists() else None,
        metadata={
            "variables": DEFAULT_ERA5_VARIABLES,
            "log_path": str(log_path),
            "request_id": request_id,
        },
    )

    status = "downloaded" if output_path.exists() else "accepted"
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO era5_requests (
                study_area_id, year, month, variables, request_id, status,
                output_path, request_payload, raw_asset_id
            )
            VALUES (%s, %s, %s, %s::jsonb, %s, %s, %s, %s::jsonb, %s)
            ON CONFLICT (study_area_id, year, month) DO UPDATE
            SET variables = EXCLUDED.variables,
                request_id = EXCLUDED.request_id,
                status = EXCLUDED.status,
                output_path = EXCLUDED.output_path,
                request_payload = EXCLUDED.request_payload,
                raw_asset_id = EXCLUDED.raw_asset_id
            """,
            (
                study_area_id,
                2025,
                1,
                json.dumps(DEFAULT_ERA5_VARIABLES),
                request_id,
                status,
                str(output_path),
                json.dumps(
                    {
                        "year": 2025,
                        "month": 1,
                        "variables": DEFAULT_ERA5_VARIABLES,
                    }
                ),
                raw_asset_id,
            ),
        )


def upsert_noaa_files(conn: psycopg.Connection, *, noaa_dir: Path) -> None:
    for filename, source_url in NOAA_FILE_URLS.items():
        local_path = noaa_dir / filename
        raw_asset_id = upsert_raw_asset(
            conn,
            source_type="noaa",
            dataset_name="noaa-global-co2",
            external_id=filename,
            asset_name=filename,
            local_path=str(local_path.resolve()) if local_path.exists() else str(local_path),
            remote_uri=source_url,
            format_name="csv",
            size_bytes=local_path.stat().st_size if local_path.exists() else None,
            metadata={"source_url": source_url},
        )
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO noaa_files (dataset_name, source_url, local_path, raw_asset_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (dataset_name) DO UPDATE
                SET source_url = EXCLUDED.source_url,
                    local_path = EXCLUDED.local_path,
                    raw_asset_id = EXCLUDED.raw_asset_id
                """,
                (filename, source_url, str(local_path), raw_asset_id),
            )


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    env = load_env(project_root)

    sentinel_catalog_path = project_root / args.sentinel_catalog_json
    sentinel_plan_path = project_root / args.sentinel_plan_json
    era5_output_path = project_root / args.era5_output_path
    era5_log_path = project_root / args.era5_log_path
    noaa_dir = project_root / args.noaa_dir

    conn = connect_db(env)
    try:
        study_area_id = ensure_study_area(
            conn,
            name=args.area_name,
            north=args.north,
            west=args.west,
            south=args.south,
            east=args.east,
        )
        upsert_sentinel_catalog(conn, study_area_id=study_area_id, catalog_path=sentinel_catalog_path)
        upsert_sentinel_plan(conn, study_area_id=study_area_id, plan_path=sentinel_plan_path)
        upsert_era5_request(
            conn,
            study_area_id=study_area_id,
            output_path=era5_output_path,
            log_path=era5_log_path,
        )
        upsert_noaa_files(conn, noaa_dir=noaa_dir)
        conn.commit()
    finally:
        conn.close()

    print("Metadata loaded into PostgreSQL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
