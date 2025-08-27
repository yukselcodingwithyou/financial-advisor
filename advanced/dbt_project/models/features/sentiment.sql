-- Sentiment Features  
-- News sentiment, analyst sentiment, and positioning indicators

SELECT 
    symbol,
    date,
    -- News sentiment
    news_sentiment_score,
    news_sentiment_volume,
    news_sentiment_change = news_sentiment_score - LAG(news_sentiment_score, 5) OVER (PARTITION BY symbol ORDER BY date),
    -- Analyst sentiment
    analyst_rating_avg,
    analyst_revision_ratio,
    target_price_return = (target_price_avg / current_price - 1),
    -- Social media sentiment
    social_sentiment_score,
    social_mention_volume,
    -- Put/call ratio (for options)
    put_call_ratio,
    put_call_ratio_ma = AVG(put_call_ratio) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW),
    -- Insider trading
    insider_buy_sell_ratio,
    -- Short interest
    short_interest_ratio,
    short_interest_change = short_interest_ratio - LAG(short_interest_ratio, 21) OVER (PARTITION BY symbol ORDER BY date),
    -- Composite sentiment score
    (
        COALESCE(news_sentiment_score * 0.3, 0) +
        COALESCE(social_sentiment_score * 0.2, 0) +
        COALESCE((analyst_rating_avg - 3) / 2 * 0.25, 0) +  -- Convert 1-5 scale to sentiment
        COALESCE(-1 * (put_call_ratio - 1) * 0.15, 0) +     -- Higher put/call = negative sentiment
        COALESCE(insider_buy_sell_ratio * 0.1, 0)
    ) as composite_sentiment_score,
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('sentiment_data', 'daily_sentiment') }}
WHERE date >= CURRENT_DATE - INTERVAL '2 years'