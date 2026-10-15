CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    operation VARCHAR(50) NOT NULL,
    algorithm VARCHAR(30),
    status VARCHAR(20) NOT NULL DEFAULT 'success',
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
ON audit_logs(created_at DESC);

INSERT INTO audit_logs (operation, algorithm, status, details)
VALUES (
    'SYSTEM_INIT',
    'N/A',
    'success',
    'SecurePass database initialized successfully'
);
