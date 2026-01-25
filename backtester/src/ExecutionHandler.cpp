
#include "ExecutionHandler.h"

ExecutionHandler::ExecutionHandler(double slippage, double commission)
    : slippage(slippage), commission(commission) {}

double ExecutionHandler::calculate_commission(double quantity, double share_price) {
    double commission_cost = commission * std::abs(quantity);

    double total_cost = quantity * share_price;

    return std::min(0.01 * total_cost, commission_cost);
}

Fill ExecutionHandler::execute_order(std::shared_ptr<Order> order, double share_price) {
    double commission = calculate_commission(order->quantity, share_price);

    return Fill{order->ticker, order->quantity, share_price, commission};
}

std::vector<std::shared_ptr<Fill>> ExecutionHandler::on_market_update(std::shared_ptr<MarketEvent> update) {
    // Update current prices and execute orders
    std::unordered_map<std::string, Bar>* bars = &update->bars;

    std::vector<std::shared_ptr<Fill>> fills;

    for (const std::shared_ptr<Order> order: pending_orders) {
        auto it = bars->find(order->ticker);
        if (it != bars->end()) {
            Bar* bar = &it->second;

            if (order->order_type == OrderType::MARKET) {
                // Execute at the open price
                Fill fill = execute_order(order, bar->open);
                std::shared_ptr<Fill> fill_ptr = std::make_shared<Fill>(fill);

                fills.push_back(fill_ptr);

                continue;
            }

            if (order->direction == Direction::BUY) {
                // If price drops below limit, then execute
                if (bar->low <= order->limit_price) {
                    Fill fill = execute_order(order, order->limit_price);
                    std::shared_ptr<Fill> fill_ptr = std::make_shared<Fill>(fill);

                    fills.push_back(fill_ptr);
                    continue;
                }
            }

            else if (order->direction == Direction::SELL) {
                if (bar->high >= order->limit_price) {
                    Fill fill = execute_order(order, order->limit_price);
                    std::shared_ptr<Fill> fill_ptr = std::make_shared<Fill>(fill);

                    fills.push_back(fill_ptr);
                    continue;
                }
            }
        }

        // Send empty FillEvent
        std::shared_ptr<Fill> fill_ptr = std::make_shared<Fill>(Fill{order->ticker, 0, 0, 0});

        fills.push_back(fill_ptr);
    }

    return fills;
}

void ExecutionHandler::submit_orders(const std::vector<std::shared_ptr<Order>>& orders) {
    pending_orders.insert(pending_orders.end(), orders.begin(), orders.end());
}