-- Database initialization script
-- This file is automatically run when the PostgreSQL container starts

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE grc_governance TO grc_user;

-- Note: Tables will be created by SQLAlchemy models when the backend starts
