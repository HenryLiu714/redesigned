#pragma once

#include <deque>
#include <memory>

#include "Event.h"
#include "Types.h"

class EventSink {
    public:
        virtual void publish(std::unique_ptr<Event> event) = 0;
};

// TODO: add logging
struct Context {
    EventSink* sink;
};