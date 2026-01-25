#include "Engine.h"

Engine::Engine(const EngineConfig& config_, std::shared_ptr<DataHandler> data_handler_) {
    config = config_;
    data_handler = data_handler_;

    execution_handler = std::make_shared<ExecutionHandler>();
    event_queue = {};
}

void Engine::set_config(const EngineConfig& config_) {
    config = config_;
}

void Engine::set_data_handler(std::shared_ptr<DataHandler> data_handler_) {
    data_handler = data_handler_;
}

void Engine::set_strategy(std::shared_ptr<Strategy> strategy_) {
    strategy = strategy_;
}

void Engine::set_portfolio(std::shared_ptr<Portfolio> portfolio_) {
    portfolio = portfolio_;
}

void Engine::run_backtest() {
    // 1. Initialize strategy
    strategy->on_start();

    // 2. Start backtest
    while (data_handler->has_next()) {
        // Queue should be empty at this point
        std::shared_ptr<MarketEvent> update = data_handler->next();

        // 3. Execute any orders
        execution_handler->on_market_update(update);

        // 4. Call strategy and generate any signals
        std::vector<std::shared_ptr<Signal>> signals = strategy->on_update(update);

        // 5. Send signals to portfolio
        portfolio->on_signals(signals);

        // 6. Receive any new orders from the portfolio
        std::vector<std::shared_ptr<Order>> orders = portfolio->send_orders();

        // 7. Submit orders to execution handler
        execution_handler->submit_orders(orders);
    }
}