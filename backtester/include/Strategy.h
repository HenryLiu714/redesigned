#pragma once

#include "Event.h"
#include "Context.h"

class Strategy {
    public:
        virtual ~Strategy();

        virtual void on_start();

        // Called on universe update, returns any signals
        virtual void on_update(const MarketEvent& event);

        void set_context(Context* context_);

    private:
        Context* context = nullptr;
        void send_signal(std::unique_ptr<Signal> signal);
};