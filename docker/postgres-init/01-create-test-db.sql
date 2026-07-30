-- Runs once when the postgres container's data directory is first initialized.
-- Creates a separate database for the integration test suite so tests never
-- touch dev data.
CREATE DATABASE billwise_test;
