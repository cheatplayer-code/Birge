-- ML Layer Database Schema for Birge
-- Enables pgvector extension and creates tables for recommendation system

-- Enable pgvector extension for embeddings (optional - fallback uses deterministic vectors)
CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;

-- Users table with adaptive interest weights stored as jsonb
CREATE TABLE IF NOT EXISTS public.users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT,
  city TEXT,
  budget_tier TEXT CHECK (budget_tier IN ('low', 'mid', 'high')),
  interests TEXT[] DEFAULT '{}',
  interest_weights JSONB DEFAULT '{}'::jsonb,
  sim_verified BOOLEAN DEFAULT FALSE,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Products table with localization and price waterfall
CREATE TABLE IF NOT EXISTS public.products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_marketplace TEXT,
  name_ru TEXT NOT NULL,
  name_kk TEXT,
  description_ru TEXT,
  description_kk TEXT,
  category TEXT NOT NULL,
  tags TEXT[] DEFAULT '{}',
  retail_price_kzt INTEGER NOT NULL,
  group_price_kzt INTEGER NOT NULL,
  original_price_usd NUMERIC(10, 2),
  weight_kg NUMERIC(8, 2),
  cargo_price_kzt INTEGER,
  image_url TEXT,
  embedding extensions.vector(12), -- Optional 12-dimensional embedding
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deals table with dynamic momentum calculation (no stored momentum_score)
CREATE TABLE IF NOT EXISTS public.deals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID REFERENCES public.products(id) ON DELETE CASCADE,
  city TEXT NOT NULL,
  current_participants INTEGER DEFAULT 0,
  target_participants INTEGER NOT NULL,
  tiers JSONB DEFAULT '[]'::jsonb,
  deadline TIMESTAMPTZ,
  status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled', 'expired')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Deal members (participants) table
CREATE TABLE IF NOT EXISTS public.deal_members (
  deal_id UUID REFERENCES public.deals(id) ON DELETE CASCADE,
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (deal_id, user_id)
);

-- Events table for tracking user interactions
CREATE TABLE IF NOT EXISTS public.events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL CHECK (event_type IN ('view', 'click', 'join', 'share')),
  product_id UUID REFERENCES public.products(id) ON DELETE SET NULL,
  deal_id UUID REFERENCES public.deals(id) ON DELETE SET NULL,
  category TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_city ON public.users(city);
CREATE INDEX IF NOT EXISTS idx_users_interests ON public.users USING GIN(interests);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category);
CREATE INDEX IF NOT EXISTS idx_products_tags ON public.products USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_products_embedding ON public.products USING ivfflat(embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_deals_status ON public.deals(status);
CREATE INDEX IF NOT EXISTS idx_deals_city ON public.deals(city);
CREATE INDEX IF NOT EXISTS idx_deals_deadline ON public.deals(deadline);
CREATE INDEX IF NOT EXISTS idx_deal_members_user ON public.deal_members(user_id);
CREATE INDEX IF NOT EXISTS idx_events_user_id ON public.events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON public.events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_created_at ON public.events(created_at);

-- Trigger to update deals.current_participants after insert/delete on deal_members
CREATE OR REPLACE FUNCTION update_deal_participants()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE public.deals
    SET current_participants = current_participants + 1,
        updated_at = NOW()
    WHERE id = NEW.deal_id;
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE public.deals
    SET current_participants = GREATEST(0, current_participants - 1),
        updated_at = NOW()
    WHERE id = OLD.deal_id;
    RETURN OLD;
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_deal_participants ON public.deal_members;
CREATE TRIGGER trg_update_deal_participants
  AFTER INSERT OR DELETE ON public.deal_members
  FOR EACH ROW
  EXECUTE FUNCTION update_deal_participants();

-- Realtime publication for deals and deal_members (safe approach)
-- Note: If supabase_realtime already exists, Supabase dashboard can enable Realtime manually.
-- Only add tables if the publication exists, otherwise skip silently.
DO $$
BEGIN
  -- Check if publication exists before altering
  IF EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'supabase_realtime') THEN
    ALTER PUBLICATION supabase_realtime ADD TABLE public.deals;
    ALTER PUBLICATION supabase_realtime ADD TABLE public.deal_members;
  END IF;
END $$;

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON public.users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_products_updated_at BEFORE UPDATE ON public.products
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_deals_updated_at BEFORE UPDATE ON public.deals
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE public.users IS 'User profiles with adaptive interest weights in interest_weights jsonb';
COMMENT ON COLUMN public.users.interest_weights IS 'Adaptive category weights updated by events (view: +0.08, click: +0.30, join: +0.60, share: +0.20)';
COMMENT ON TABLE public.products IS 'Products with localization (ru/kk) and price waterfall';
COMMENT ON COLUMN public.products.embedding IS 'Optional 12-dimensional vector for similarity matching';
COMMENT ON TABLE public.deals IS 'Deals with dynamically calculated momentum from participants/deadline/tiers';
COMMENT ON COLUMN public.deals.current_participants IS 'Auto-updated via trigger from deal_members';
COMMENT ON TABLE public.events IS 'User interaction events for adaptive recommendations';
