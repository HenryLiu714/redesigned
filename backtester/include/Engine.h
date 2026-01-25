#pragma once

#include <memory>
#include <deque>

#include "Event.h"
#include "Strategy.h"
#include "Portfolio.h"
#include "DataHandler.h"
#include "ExecutionHandler.h"
#include "Context.h"

struct EngineConfig {
    double initial_capital = 100000;
    std::string start_date = "2016-01-01";
    std::string end_date = "";
    double commission = 0;
    double slippage = 0;
    bool verbose = false;
};

class Engine : public EventSink {
    public:
        Engine(const EngineConfig& config_, std::shared_ptr<DataHandler> data_handler_);
        ~Engine();

        void publish(std::unique_ptr<Event> event);

        void set_config(const EngineConfig& config_);
        void set_data_handler(std::shared_ptr<DataHandler> data_handler_);
        void set_strategy(std::shared_ptr<Strategy> strategy_);
        void set_portfolio(std::shared_ptr<Portfolio> portfolio_);

        void run_backtest();

    private:
        EngineConfig config;

        std::shared_ptr<DataHandler> data_handler;
        std::shared_ptr<Strategy> strategy;
        std::shared_ptr<Portfolio> portfolio;

        std::unique_ptr<ExecutionHandler> execution_handler;

        std::deque<std::unique_ptr<Event>> event_queue;
};