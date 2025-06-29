-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Cooperatives table
CREATE TABLE cooperatives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    super_admin_id UUID
);

-- Users table (linked to Supabase Auth)
CREATE TABLE users (
    id UUID PRIMARY KEY, -- Managed by Supabase Auth
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    name VARCHAR(255) NOT NULL,
    cooperative_id UUID REFERENCES cooperatives(id),
    role VARCHAR(20) CHECK (role IN ('super_admin', 'admin', 'member')),
    status VARCHAR(20) CHECK (status IN ('pending', 'active', 'inactive')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Contributions table
CREATE TABLE contributions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    cooperative_id UUID REFERENCES cooperatives(id),
    amount DECIMAL(10,2) NOT NULL,
    type VARCHAR(20) CHECK (type IN ('weekly', 'monthly')),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('paid', 'pending'))
);

-- Dues table
CREATE TABLE dues (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cooperative_id UUID REFERENCES cooperatives(id),
    user_id UUID REFERENCES users(id),
    amount DECIMAL(10,2) NOT NULL,
    due_date TIMESTAMP NOT NULL,
    status VARCHAR(20) CHECK (status IN ('paid', 'pending', 'overdue'))
);

-- Penalties table
CREATE TABLE penalties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    cooperative_id UUID REFERENCES cooperatives(id),
    amount DECIMAL(10,2) NOT NULL,
    reason TEXT,
    date_issued TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) CHECK (status IN ('paid', 'pending'))
);

-- Transactions table
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cooperative_id UUID REFERENCES cooperatives(id),
    user_id UUID REFERENCES users(id) NULL, -- Nullable for cooperative-wide transactions
    amount DECIMAL(10,2) NOT NULL,
    type VARCHAR(20) CHECK (type IN ('contribution', 'due', 'penalty', 'registration', 'other')),
    paystack_ref VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Income/Expenses table
CREATE TABLE income_expenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cooperative_id UUID REFERENCES cooperatives(id),
    type VARCHAR(20) CHECK (type IN ('income', 'expense')),
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- Tasks table (for payment tracking, e.g., levies, projects)
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cooperative_id UUID REFERENCES cooperatives(id),
    name VARCHAR(255) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payment Tracking table
CREATE TABLE payment_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cooperative_id UUID REFERENCES cooperatives(id),
    user_id UUID REFERENCES users(id),
    task_id UUID REFERENCES tasks(id),
    amount_due DECIMAL(10,2) NOT NULL,
    amount_paid DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) CHECK (status IN ('fully_paid', 'partial', 'unpaid')),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Meetings table
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cooperative_id UUID REFERENCES cooperatives(id),
    title VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    created_by UUID REFERENCES users(id)
);

-- Attendance table
CREATE TABLE attendance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cooperative_id UUID REFERENCES cooperatives(id),
    user_id UUID REFERENCES users(id),
    meeting_id UUID REFERENCES meetings(id),
    status VARCHAR(20) CHECK (status IN ('present', 'absent')),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);