-- Migration: Create trigger for automatic stock reduction on billing
-- Created: 2025-10-15
-- Description: Auto-reduce stock when GST or Non-GST bill is created

-- UP Migration

-- Function to reduce stock on billing
CREATE OR REPLACE FUNCTION reduce_stock_on_billing()
RETURNS TRIGGER AS $$
DECLARE
    item JSONB;
BEGIN
    -- Loop through each item in the bill
    FOR item IN SELECT * FROM jsonb_array_elements(NEW.items)
    LOOP
        -- Reduce stock quantity for this product
        UPDATE stock_entry
        SET quantity = quantity - (item->>'quantity')::INTEGER,
            updated_at = NOW()
        WHERE product_id = (item->>'product_id')::UUID
          AND client_id = NEW.client_id;

        -- Check if update was successful
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Product % not found for client_id %',
                (item->>'product_id'), NEW.client_id;
        END IF;
    END LOOP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for GST billing
CREATE TRIGGER trigger_reduce_stock_gst_billing
    AFTER INSERT ON gst_billing
    FOR EACH ROW
    WHEN (NEW.status = 'final')
    EXECUTE FUNCTION reduce_stock_on_billing();

-- Create trigger for Non-GST billing
CREATE TRIGGER trigger_reduce_stock_non_gst_billing
    AFTER INSERT ON non_gst_billing
    FOR EACH ROW
    WHEN (NEW.status = 'final')
    EXECUTE FUNCTION reduce_stock_on_billing();

-- Add comments
COMMENT ON FUNCTION reduce_stock_on_billing() IS 'Auto-reduce stock when bill is created with status=final';

-- DOWN Migration (Rollback)
-- DROP TRIGGER IF EXISTS trigger_reduce_stock_non_gst_billing ON non_gst_billing;
-- DROP TRIGGER IF EXISTS trigger_reduce_stock_gst_billing ON gst_billing;
-- DROP FUNCTION IF EXISTS reduce_stock_on_billing();
