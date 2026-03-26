import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { MapPin, Calendar, Star } from "lucide-react";
import { lifeEventsApi, LifeEvent } from "@/services/api";

const Timeline = () => {
  const [events, setEvents] = useState<LifeEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<LifeEvent | null>(null);

  useEffect(() => {
    loadEvents();
  }, []);

  const loadEvents = async () => {
    try {
      setLoading(true);
      const eventsData = await lifeEventsApi.getAll();
      setEvents(eventsData);
    } catch (error) {
      console.error('Failed to load events:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <section className="py-16 px-4 bg-gradient-to-b from-white to-gray-50">
        <div className="max-w-4xl mx-auto">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
              <Calendar className="w-8 h-8 text-gray-400 animate-pulse" />
            </div>
            <p className="text-gray-500 text-lg">Loading timeline...</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-white to-gray-50">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Life Journey
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            A timeline of precious moments and milestones that shaped a beautiful life
          </p>
        </div>

        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-1/2 transform -translate-x-1/2 w-1 h-full bg-gray-200"></div>

          {/* Timeline events */}
          <div className="space-y-12">
            {events.map((event, index) => (
              <div
                key={event.id}
                className={`relative flex items-center ${
                  index % 2 === 0 ? 'justify-start' : 'justify-end'
                }`}
              >
                {/* Event card */}
                <div className={`w-5/12 ${index % 2 === 0 ? 'pr-8 text-right' : 'pl-8'}`}>
                  <Card 
                    className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
                      selectedEvent?.id === event.id ? 'ring-2 ring-blue-500 shadow-lg' : ''
                    }`}
                    onClick={() => setSelectedEvent(selectedEvent?.id === event.id ? null : event)}
                  >
                    <CardContent className="p-6">
                      <div className="flex items-center gap-2 mb-3">
                        <Calendar className="w-4 h-4 text-blue-500" />
                        <span className="text-sm font-semibold text-blue-600">
                          {event.event_year}
                        </span>
                        {event.is_featured && (
                          <Star className="w-4 h-4 text-yellow-500 fill-yellow-500" />
                        )}
                      </div>
                      
                      <h3 className="text-xl font-bold text-gray-900 mb-2">
                        {event.title}
                      </h3>
                      
                      {event.description && (
                        <p className="text-gray-600 mb-3">
                          {event.description}
                        </p>
                      )}
                      
                      {event.location_name && (
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                          <MapPin className="w-4 h-4" />
                          <span>{event.location_name}</span>
                        </div>
                      )}
                      
                      {event.coordinates && (
                        <div className="mt-2 text-xs text-gray-400">
                          📍 {event.coordinates[0].toFixed(4)}, {event.coordinates[1].toFixed(4)}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {/* Timeline dot */}
                <div className="absolute left-1/2 transform -translate-x-1/2 w-4 h-4 bg-blue-500 rounded-full border-4 border-white shadow-md"></div>
              </div>
            ))}
          </div>
        </div>

        {/* Selected event details */}
        {selectedEvent && (
          <div className="mt-12 p-6 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-2xl font-bold text-blue-900">
                {selectedEvent.title}
              </h3>
              <button
                onClick={() => setSelectedEvent(null)}
                className="text-blue-600 hover:text-blue-800"
              >
                ✕
              </button>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Calendar className="w-5 h-5 text-blue-600" />
                  <span className="font-semibold text-blue-800">
                    {selectedEvent.event_year}
                  </span>
                </div>
                
                {selectedEvent.description && (
                  <p className="text-gray-700 mb-4">
                    {selectedEvent.description}
                  </p>
                )}
                
                {selectedEvent.location_name && (
                  <div className="flex items-center gap-2 text-gray-600">
                    <MapPin className="w-4 h-4" />
                    <span>{selectedEvent.location_name}</span>
                  </div>
                )}
              </div>
              
              {selectedEvent.coordinates && (
                <div className="bg-white p-4 rounded-lg">
                  <h4 className="font-semibold text-gray-800 mb-2">Location</h4>
                  <div className="text-sm text-gray-600">
                    <p>Latitude: {selectedEvent.coordinates[0]}</p>
                    <p>Longitude: {selectedEvent.coordinates[1]}</p>
                  </div>
                  <a
                    href={`https://maps.google.com/?q=${selectedEvent.coordinates[0]},${selectedEvent.coordinates[1]}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-block mt-2 text-blue-600 hover:text-blue-800 text-sm"
                  >
                    View on Google Maps →
                  </a>
                </div>
              )}
            </div>
          </div>
        )}

        {events.length === 0 && (
          <div className="text-center py-12">
            <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No life events yet</p>
            <p className="text-gray-400 mt-2">Timeline will appear here once events are added</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default Timeline;
