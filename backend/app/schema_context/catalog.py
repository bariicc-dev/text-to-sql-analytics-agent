from app.schema_context.models import ColumnContext, SchemaContext, TableContext

DEMO_SCHEMA_CONTEXT = SchemaContext(
    database_name="demo_ecommerce",
    description="Small synthetic e-commerce database for safe Text-to-SQL demos and backend tests.",
    business_rules=[
        "Revenue is based on order item quantity multiplied by unit price.",
        "Completed and refunded orders are included in revenue examples unless a query says otherwise.",
        "Refund analysis uses the refunds table linked to orders and products.",
        "Query logs and feedback are operational tables for tracking agent behavior, not business sales tables.",
    ],
    safe_query_rules=[
        "Only read-only SELECT or WITH queries should be executed.",
        "Generated SQL must be validated before execution.",
        "Unsafe statements such as UPDATE, DELETE, DROP, INSERT, ALTER, and TRUNCATE are blocked.",
    ],
    tables=[
        TableContext(
            name="customers",
            description="Demo customers with segment, country, and creation date fields.",
            primary_key="id",
            relationships=["orders.customer_id -> customers.id", "feedback.customer_id -> customers.id"],
            common_questions=[
                "Which customer segment brings the most revenue?",
                "How many customers are in each segment?",
            ],
            columns=[
                ColumnContext(name="id", type="integer", description="Customer identifier.", is_nullable=False, is_primary_key=True, example_values=["1"]),
                ColumnContext(name="name", type="string", description="Customer display name.", is_nullable=False, example_values=["Nora Adams"]),
                ColumnContext(name="email", type="string", description="Unique customer email address.", is_nullable=False, example_values=["nora.adams@example.com"]),
                ColumnContext(name="segment", type="string", description="Customer segment used for analytics grouping.", is_nullable=False, example_values=["Consumer", "Small Business", "Enterprise"]),
                ColumnContext(name="country", type="string", description="Customer country.", is_nullable=False, example_values=["France", "Germany"]),
                ColumnContext(name="created_at", type="date", description="Date the customer record was created.", is_nullable=False, example_values=["2025-01-08"]),
            ],
        ),
        TableContext(
            name="products",
            description="Demo products with category, price, and cost fields.",
            primary_key="id",
            relationships=["order_items.product_id -> products.id", "refunds.product_id -> products.id"],
            common_questions=[
                "What are the top products by revenue?",
                "Which product categories generate the most revenue?",
            ],
            columns=[
                ColumnContext(name="id", type="integer", description="Product identifier.", is_nullable=False, is_primary_key=True, example_values=["1"]),
                ColumnContext(name="name", type="string", description="Product name.", is_nullable=False, example_values=["Everyday Backpack"]),
                ColumnContext(name="category", type="string", description="Product category for grouping analytics.", is_nullable=False, example_values=["Bags", "Electronics"]),
                ColumnContext(name="unit_price", type="numeric", description="Default sale price for the product.", is_nullable=False, example_values=["79.00"]),
                ColumnContext(name="unit_cost", type="numeric", description="Default product cost used for margin-style analysis later.", is_nullable=False, example_values=["32.00"]),
            ],
        ),
        TableContext(
            name="orders",
            description="Order headers representing customer purchases across sales channels.",
            primary_key="id",
            relationships=["orders.customer_id -> customers.id", "order_items.order_id -> orders.id", "refunds.order_id -> orders.id"],
            common_questions=[
                "What is monthly revenue?",
                "How many orders were placed by channel?",
            ],
            columns=[
                ColumnContext(name="id", type="integer", description="Order identifier.", is_nullable=False, is_primary_key=True, example_values=["1"]),
                ColumnContext(name="customer_id", type="integer", description="Customer who placed the order.", is_nullable=False, is_foreign_key=True, references="customers.id", example_values=["1"]),
                ColumnContext(name="order_date", type="date", description="Date the order was placed.", is_nullable=False, example_values=["2025-04-02"]),
                ColumnContext(name="status", type="string", description="Order status, such as completed or refunded.", is_nullable=False, example_values=["completed", "refunded"]),
                ColumnContext(name="channel", type="string", description="Sales channel for the order.", is_nullable=False, example_values=["web", "sales", "partner"]),
            ],
        ),
        TableContext(
            name="order_items",
            description="Line items showing which products were included in each order.",
            primary_key="id",
            relationships=["order_items.order_id -> orders.id", "order_items.product_id -> products.id"],
            common_questions=[
                "Which products sold the most units?",
                "Which products generated the most revenue?",
            ],
            columns=[
                ColumnContext(name="id", type="integer", description="Order item identifier.", is_nullable=False, is_primary_key=True, example_values=["1"]),
                ColumnContext(name="order_id", type="integer", description="Order containing this item.", is_nullable=False, is_foreign_key=True, references="orders.id", example_values=["1"]),
                ColumnContext(name="product_id", type="integer", description="Product sold in this line item.", is_nullable=False, is_foreign_key=True, references="products.id", example_values=["1"]),
                ColumnContext(name="quantity", type="integer", description="Number of product units sold.", is_nullable=False, example_values=["2"]),
                ColumnContext(name="unit_price", type="numeric", description="Sale price captured on the order item.", is_nullable=False, example_values=["79.00"]),
            ],
        ),
        TableContext(
            name="refunds",
            description="Refund records linked to refunded orders and products.",
            primary_key="id",
            relationships=["refunds.order_id -> orders.id", "refunds.product_id -> products.id"],
            common_questions=[
                "What is the refund rate?",
                "Which categories have refunds?",
            ],
            columns=[
                ColumnContext(name="id", type="integer", description="Refund identifier.", is_nullable=False, is_primary_key=True, example_values=["1"]),
                ColumnContext(name="order_id", type="integer", description="Order connected to the refund.", is_nullable=False, is_foreign_key=True, references="orders.id", example_values=["6"]),
                ColumnContext(name="product_id", type="integer", description="Product connected to the refund.", is_nullable=False, is_foreign_key=True, references="products.id", example_values=["4"]),
                ColumnContext(name="refund_date", type="date", description="Date the refund was recorded.", is_nullable=False, example_values=["2025-06-20"]),
                ColumnContext(name="amount", type="numeric", description="Refund amount.", is_nullable=False, example_values=["229.00"]),
                ColumnContext(name="reason", type="string", description="Reason recorded for the refund.", is_nullable=False, example_values=["Customer returned the item"]),
            ],
        ),
        TableContext(
            name="query_logs",
            description="History of chat questions, generated SQL, safety status, and errors.",
            primary_key="id",
            relationships=["feedback.query_log_id -> query_logs.id"],
            common_questions=[
                "Which chat interactions failed?",
                "How often are questions blocked or unsupported?",
            ],
            columns=[
                ColumnContext(name="id", type="integer", description="Query log identifier.", is_nullable=False, is_primary_key=True, example_values=["1"]),
                ColumnContext(name="question", type="text", description="Original user question sent to chat.", is_nullable=False),
                ColumnContext(name="generated_sql", type="text", description="SQL generated or selected for the question when available.", is_nullable=True),
                ColumnContext(name="safety_status", type="string", description="Safety result such as safe, blocked, not_generated, or error.", is_nullable=False, example_values=["safe", "blocked"]),
                ColumnContext(name="error_message", type="text", description="Clean error message when the interaction failed.", is_nullable=True),
                ColumnContext(name="created_at", type="datetime", description="Timestamp when the query log was created.", is_nullable=False),
            ],
        ),
        TableContext(
            name="feedback",
            description="Feedback ratings and comments linked to query logs.",
            primary_key="id",
            relationships=["feedback.query_log_id -> query_logs.id", "feedback.customer_id -> customers.id"],
            common_questions=[
                "Which answers received low ratings?",
                "Which query logs have feedback?",
            ],
            columns=[
                ColumnContext(name="id", type="integer", description="Feedback identifier.", is_nullable=False, is_primary_key=True, example_values=["1"]),
                ColumnContext(name="query_log_id", type="integer", description="Query log being rated.", is_nullable=False, is_foreign_key=True, references="query_logs.id", example_values=["1"]),
                ColumnContext(name="customer_id", type="integer", description="Optional customer linked to the feedback.", is_nullable=True, is_foreign_key=True, references="customers.id"),
                ColumnContext(name="rating", type="integer", description="Rating from 1 to 5.", is_nullable=False, example_values=["5"]),
                ColumnContext(name="comment", type="text", description="Optional feedback comment.", is_nullable=True, example_values=["Useful answer"]),
                ColumnContext(name="created_at", type="datetime", description="Timestamp when feedback was created.", is_nullable=False),
            ],
        ),
    ],
)
