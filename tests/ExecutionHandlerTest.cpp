#include <gtest/gtest.h>
#include "ExecutionHandler.h"

class ExecutionHandlerTest : public ::testing::Test {
protected:
    ExecutionHandlerTest() : handler(0.0005, 0.35) {}

    ExecutionHandler handler;

    // Helper to create a market event with a bar
    std::shared_ptr<MarketEvent> createMarketEvent(
        const std::string& ticker, double open, double high, double low, double close, double volume = 1000) {
        auto event = std::make_shared<MarketEvent>();
        event->bars[ticker] = Bar{ticker, 0, open, high, low, close, volume};
        return event;
    }

    // Helper to create a market order
    std::shared_ptr<Order> createMarketOrder(
        const std::string& ticker, Direction dir, double quantity) {
        return std::make_shared<Order>(Order{
            OrderType::MARKET,
            ticker,
            dir,
            quantity,
            0 // limit price not used for market orders
        });
    }

    // Helper to create a limit order
    std::shared_ptr<Order> createLimitOrder(
        const std::string& ticker, Direction dir, double quantity, double limitPrice) {
        return std::make_shared<Order>(Order{
            OrderType::LIMIT,
            ticker,
            dir,
            quantity,
            limitPrice
        });
    }
};

// ==================== Market Order Tests ====================

TEST_F(ExecutionHandlerTest, MarketOrder_BuyExecutesAtOpenPrice) {
    auto order = createMarketOrder("AAPL", Direction::BUY, 100);
    handler.submit_order(order);

    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 148.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->ticker, "AAPL");
    EXPECT_EQ(fills[0]->quantity, 100);
    EXPECT_EQ(fills[0]->fill_price, 150.0);
    EXPECT_GT(fills[0]->commission, 0);
}

TEST_F(ExecutionHandlerTest, MarketOrder_SellExecutesAtOpenPrice) {
    auto order = createMarketOrder("AAPL", Direction::SELL, 50);
    handler.submit_order(order);

    auto market_event = createMarketEvent("AAPL", 200.0, 205.0, 198.0, 202.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->ticker, "AAPL");
    EXPECT_EQ(fills[0]->quantity, 50);
    EXPECT_EQ(fills[0]->fill_price, 200.0);
}

TEST_F(ExecutionHandlerTest, MarketOrder_MultipleOrdersInSingleUpdate) {
    auto order1 = createMarketOrder("AAPL", Direction::BUY, 100);
    auto order2 = createMarketOrder("MSFT", Direction::SELL, 50);
    handler.submit_order(order1);
    handler.submit_order(order2);

    auto market_event = std::make_shared<MarketEvent>();
    market_event->bars["AAPL"] = Bar{"AAPL", 0, 150.0, 155.0, 148.0, 152.0, 1000};
    market_event->bars["MSFT"] = Bar{"MSFT", 0, 300.0, 305.0, 298.0, 302.0, 1000};

    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 2);
    EXPECT_EQ(fills[0]->ticker, "AAPL");
    EXPECT_EQ(fills[1]->ticker, "MSFT");
}

// ==================== Limit Order Tests ====================

TEST_F(ExecutionHandlerTest, LimitOrder_BuyExecutesWhenPriceDropsBelowLimit) {
    auto order = createLimitOrder("AAPL", Direction::BUY, 100, 148.0);
    handler.submit_order(order);

    // bar low is 145, which is below limit of 148
    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 145.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->fill_price, 148.0); // executed at limit price
}

TEST_F(ExecutionHandlerTest, LimitOrder_BuyDoesNotExecuteWhenPriceAboveLimit) {
    auto order = createLimitOrder("AAPL", Direction::BUY, 100, 145.0);
    handler.submit_order(order);

    // bar low is 148, which is above limit of 145
    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 148.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->quantity, 0); // empty fill
}

TEST_F(ExecutionHandlerTest, LimitOrder_BuyExecutesAtExactLimit) {
    auto order = createLimitOrder("AAPL", Direction::BUY, 100, 148.0);
    handler.submit_order(order);

    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 148.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->quantity, 100);
}

TEST_F(ExecutionHandlerTest, LimitOrder_SellExecutesWhenPriceRisesAboveLimit) {
    auto order = createLimitOrder("AAPL", Direction::SELL, 100, 155.0);
    handler.submit_order(order);

    // bar high is 158, which is above limit of 155
    auto market_event = createMarketEvent("AAPL", 150.0, 158.0, 145.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->fill_price, 155.0);
}

TEST_F(ExecutionHandlerTest, LimitOrder_SellDoesNotExecuteWhenPriceBelowLimit) {
    auto order = createLimitOrder("AAPL", Direction::SELL, 100, 155.0);
    handler.submit_order(order);

    // bar high is 152, which is below limit of 155
    auto market_event = createMarketEvent("AAPL", 150.0, 152.0, 145.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->quantity, 0); // empty fill
}

TEST_F(ExecutionHandlerTest, LimitOrder_SellExecutesAtExactLimit) {
    auto order = createLimitOrder("AAPL", Direction::SELL, 100, 155.0);
    handler.submit_order(order);

    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 145.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->quantity, 100);
}

// ==================== Missing Ticker Tests ====================

TEST_F(ExecutionHandlerTest, OrderNotExecuted_TickerNotInMarketUpdate) {
    auto order = createMarketOrder("AAPL", Direction::BUY, 100);
    handler.submit_order(order);

    auto market_event = createMarketEvent("MSFT", 200.0, 205.0, 198.0, 202.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->ticker, "AAPL");
    EXPECT_EQ(fills[0]->quantity, 0); // empty fill
}

// ==================== Edge Cases ====================

TEST_F(ExecutionHandlerTest, NoOrdersSubmitted) {
    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 148.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 0);
}

TEST_F(ExecutionHandlerTest, EmptyMarketUpdate) {
    auto order = createMarketOrder("AAPL", Direction::BUY, 100);
    handler.submit_order(order);

    auto market_event = std::make_shared<MarketEvent>();
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->quantity, 0); // empty fill
}

TEST_F(ExecutionHandlerTest, SubmitMultipleOrdersSameTicketDifferentLimits) {
    auto order1 = createLimitOrder("AAPL", Direction::BUY, 100, 140.0);
    auto order2 = createLimitOrder("AAPL", Direction::BUY, 50, 150.0);
    handler.submit_order(order1);
    handler.submit_order(order2);

    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 145.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 2);
    EXPECT_EQ(fills[0]->quantity, 0); // first order doesn't execute (low 145 > limit 140)
    EXPECT_EQ(fills[1]->quantity, 50); // second order executes (low 145 <= limit 150)
}

TEST_F(ExecutionHandlerTest, VerySmallQuantities) {
    auto order = createMarketOrder("AAPL", Direction::BUY, 0.1);
    handler.submit_order(order);

    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 148.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->quantity, 0.1);
}

TEST_F(ExecutionHandlerTest, VeryLargeQuantities) {
    auto order = createMarketOrder("AAPL", Direction::BUY, 1000000);
    handler.submit_order(order);

    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 148.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->quantity, 1000000);
}

TEST_F(ExecutionHandlerTest, VerySmallPrices) {
    auto order = createMarketOrder("PENNY", Direction::BUY, 100);
    handler.submit_order(order);

    auto market_event = createMarketEvent("PENNY", 0.001, 0.002, 0.0005, 0.0015);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->fill_price, 0.001);
}

TEST_F(ExecutionHandlerTest, VeryLargePrices) {
    auto order = createMarketOrder("EXPENSIVE", Direction::BUY, 1);
    handler.submit_order(order);

    auto market_event = createMarketEvent("EXPENSIVE", 10000.0, 10100.0, 9900.0, 10050.0);
    auto fills = handler.on_market_update(market_event);

    EXPECT_EQ(fills.size(), 1);
    EXPECT_EQ(fills[0]->fill_price, 10000.0);
}

// ==================== Commission Verification Tests ====================

TEST_F(ExecutionHandlerTest, FillContainsCorrectCommission) {
    auto order = createMarketOrder("AAPL", Direction::BUY, 100);
    handler.submit_order(order);

    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 148.0, 152.0);
    auto fills = handler.on_market_update(market_event);

    double expectedCommission = std::min(0.01 * (100 * 150), 0.35 * 100);
    EXPECT_DOUBLE_EQ(fills[0]->commission, expectedCommission);
}

// ==================== Different Commission Rates ====================

TEST_F(ExecutionHandlerTest, CustomCommissionRate) {
    ExecutionHandler handler_custom(0.0005, 0.5);
    auto order = createMarketOrder("AAPL", Direction::BUY, 100);
    handler_custom.submit_order(order);

    auto market_event = createMarketEvent("AAPL", 150.0, 155.0, 148.0, 152.0);
    auto fills = handler_custom.on_market_update(market_event);

    double expectedCommission = std::min(0.01 * (100 * 150), 0.5 * 100); // min(150, 50) = 50
    EXPECT_DOUBLE_EQ(fills[0]->commission, expectedCommission);
}
