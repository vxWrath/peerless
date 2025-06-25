CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id VARCHAR(20) PRIMARY KEY,
    settings JSONB DEFAULT '{}',
    updated_by VARCHAR(20) DEFAULT 'website',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_guild_settings_updated_at 
    BEFORE UPDATE ON guild_settings 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();
