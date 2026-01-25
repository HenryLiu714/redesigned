
#include "ExecutionHandler.h"

ExecutionHandler::ExecutionHandler(double slippage, double commission)
    : slippage(slippage), commission(commission) {}

double ExecutionHandler::calculate_commission(double quantity, double share_price) {
    double commission_cost = commission * std::abs(quantity);

    double total_cost = quantity * share_price;

    return std::min(0.01 * total_cost, commission_cost);
}

void ExecutionHandler::execute_order(const Order& order, double share_price) {
    double commission = calculate_commission(order.quantity, share_price);
    auto fe = std::make_unique<FillEvent>();
    fe->fill = std::make_unique<Fill>(Fill{order.ticker, order.quantity, share_price, commission});
    context.sink->publish(std::move(fe));
}

void ExecutionHandler::on_market_update(const MarketEvent& update) {
    // Update current prices and execute orders
    const std::unordered_map<std::string, Bar>* bars = &update.bars;

    for (const std::unique_ptr<Order>& order: pending_orders) {
        auto it = bars->find(order->ticker);
        if (it != bars->end()) {
            const Bar* bar = &it->second;

            if (order->order_type == OrderType::MARKET) {
                // Execute at the open price
                execute_order(*order, bar->open);
                continue;
            }

            if (order->direction == Direction::BUY) {
                // If price drops below limit, then execute
                if (bar->low <= order->limit_price) {
                    execute_order(*order, order->limit_price);
                    continue;
                }
            }

            else if (order->direction == Direction::SELL) {
                if (bar->high >= order->limit_price) {
                    execute_order(*order, order->limit_price);
                    continue;
                }
            }
        }

        // Send empty FillEvent
        auto fe = std::make_unique<FillEvent>();
        fe->fill = std::make_unique<Fill>(Fill{order->ticker, 0, 0, 0});
        context.sink->publish(std::move(fe));
    }
}

void ExecutionHandler::submit_order(std::unique_ptr<Order> order) {
    pending_orders.push_back(std::move(order));
}

void ExecutionHandler::set_context(Context context_) {
    context = context_;
}