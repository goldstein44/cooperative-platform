-- 🔒 Global Admin Check (if used standalone)
-- Ensures only super_admin or admin roles can pass check
WITH CHECK (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- 📄 Policies for dues
CREATE POLICY "Members can view their dues" ON dues
FOR SELECT
USING (
  user_id = auth.uid() OR 
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

CREATE POLICY "Admins can manage dues" ON dues
FOR ALL
USING (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
)
WITH CHECK (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- ⚖️ Policies for penalties
CREATE POLICY "Members can view their penalties" ON penalties
FOR SELECT
USING (
  user_id = auth.uid() OR 
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

CREATE POLICY "Admins can manage penalties" ON penalties
FOR ALL
USING (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
)
WITH CHECK (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- 💳 Policies for transactions
CREATE POLICY "Members can view transactions" ON transactions
FOR SELECT
USING (
  user_id = auth.uid() OR 
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

CREATE POLICY "Admins can manage transactions" ON transactions
FOR ALL
USING (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
)
WITH CHECK (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- 💰 Policies for income_expenses
CREATE POLICY "All can view income_expenses" ON income_expenses
FOR SELECT
USING (
  cooperative_id = (SELECT cooperative_id FROM users WHERE id = auth.uid())
);

CREATE POLICY "Admins can manage income_expenses" ON income_expenses
FOR ALL
USING (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
)
WITH CHECK (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- 📋 Policies for tasks
CREATE POLICY "All can view tasks" ON tasks
FOR SELECT
USING (
  cooperative_id = (SELECT cooperative_id FROM users WHERE id = auth.uid())
);

CREATE POLICY "Admins can manage tasks" ON tasks
FOR ALL
USING (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
)
WITH CHECK (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- 📈 Policies for payment_tracking
CREATE POLICY "All can view payment_tracking" ON payment_tracking
FOR SELECT
USING (
  cooperative_id = (SELECT cooperative_id FROM users WHERE id = auth.uid())
);

CREATE POLICY "Admins can manage payment_tracking" ON payment_tracking
FOR ALL
USING (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
)
WITH CHECK (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- 🗓️ Policies for meetings
CREATE POLICY "All can view meetings" ON meetings
FOR SELECT
USING (
  cooperative_id = (SELECT cooperative_id FROM users WHERE id = auth.uid())
);

CREATE POLICY "Admins can manage meetings" ON meetings
FOR ALL
USING (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
)
WITH CHECK (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);

-- ✅ Policies for attendance
CREATE POLICY "All can view attendance" ON attendance
FOR SELECT
USING (
  cooperative_id = (SELECT cooperative_id FROM users WHERE id = auth.uid())
);

CREATE POLICY "Admins can manage attendance" ON attendance
FOR ALL
USING (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
)
WITH CHECK (
  (SELECT role FROM users WHERE id = auth.uid()) IN ('super_admin', 'admin')
);