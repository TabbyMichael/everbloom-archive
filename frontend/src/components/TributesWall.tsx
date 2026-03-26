import { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Heart, MessageSquare, Flame, User, Calendar, Wifi, WifiOff } from "lucide-react";
import { tributesApi, TributePublic, Tribute } from "@/services/api";
import { useWebSocket, CandleUpdate, NewTribute } from "@/services/websocket";

interface TributeFormData {
  author_name: string;
  relation_to_deceased: string;
  message: string;
  email: string;
  candle_lit: boolean;
}

const TributesWall = () => {
  const [tributes, setTributes] = useState<TributePublic[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [websocketConnected, setWebsocketConnected] = useState(false);
  const [formData, setFormData] = useState<TributeFormData>({
    author_name: '',
    relation_to_deceased: '',
    message: '',
    email: '',
    candle_lit: false
  });

  const { connect, disconnect, isConnected, joinTributesRoom, leaveTributesRoom, onCandleUpdate, onNewTribute } = useWebSocket();

  useEffect(() => {
    loadTributes();
    setupWebSocket();
    
    return () => {
      leaveTributesRoom();
      disconnect();
    };
  }, []);

  const setupWebSocket = async () => {
    try {
      await connect();
      setWebsocketConnected(true);
      joinTributesRoom();
      
      // Listen for candle updates
      onCandleUpdate((data: CandleUpdate) => {
        setTributes(prev => 
          prev.map(tribute => 
            tribute.id === data.tribute_id 
              ? { ...tribute, candle_lit: data.candle_lit }
              : tribute
          )
        );
      });
      
      // Listen for new tributes
      onNewTribute((data: NewTribute) => {
        setTributes(prev => [data, ...prev]);
      });
      
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      setWebsocketConnected(false);
    }
  };

  const loadTributes = async () => {
    try {
      setLoading(true);
      const tributesData = await tributesApi.getAll();
      setTributes(tributesData);
    } catch (error) {
      console.error('Failed to load tributes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.author_name.trim() || !formData.message.trim()) {
      return;
    }

    try {
      setSubmitting(true);
      const newTribute = await tributesApi.create(formData);
      
      // Add to local state (will show up once approved)
      if (newTribute.approved) {
        setTributes(prev => [newTribute, ...prev]);
      }
      
      // Reset form
      setFormData({
        author_name: '',
        relation_to_deceased: '',
        message: '',
        email: '',
        candle_lit: false
      });
      setShowForm(false);
      
      alert('Thank you for your tribute! It will appear here once approved.');
    } catch (error) {
      console.error('Failed to submit tribute:', error);
      alert('Failed to submit tribute. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleLightCandle = async (tributeId: string) => {
    try {
      await tributesApi.lightCandle(tributeId);
      // Update local state
      setTributes(prev => 
        prev.map(tribute => 
          tribute.id === tributeId 
            ? { ...tribute, candle_lit: true }
            : tribute
        )
      );
    } catch (error) {
      console.error('Failed to light candle:', error);
    }
  };

  if (loading) {
    return (
      <section className="py-16 px-4 bg-gradient-to-b from-gray-50 to-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
              <Heart className="w-8 h-8 text-gray-400 animate-pulse" />
            </div>
            <p className="text-gray-500 text-lg">Loading tributes...</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="py-16 px-4 bg-gradient-to-b from-gray-50 to-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Tributes Wall
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Share your memories, thoughts, and messages of love and remembrance
          </p>
        </div>

        {/* Add Tribute Button */}
        <div className="text-center mb-8">
          {/* WebSocket Connection Indicator */}
          <div className="flex items-center justify-center gap-2 mb-4">
            {websocketConnected ? (
              <div className="flex items-center gap-2 text-green-600">
                <Wifi className="w-4 h-4" />
                <span className="text-sm">Real-time updates enabled</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-gray-500">
                <WifiOff className="w-4 h-4" />
                <span className="text-sm">Real-time updates disabled</span>
              </div>
            )}
          </div>

          <Dialog open={showForm} onOpenChange={setShowForm}>
            <DialogTrigger asChild>
              <Button className="bg-blue-600 hover:bg-blue-700">
                <MessageSquare className="w-4 h-4 mr-2" />
                Leave a Tribute
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Share Your Tribute</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="author_name">Your Name *</Label>
                  <Input
                    id="author_name"
                    value={formData.author_name}
                    onChange={(e) => setFormData(prev => ({ ...prev, author_name: e.target.value }))}
                    placeholder="Enter your name"
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="relation_to_deceased">Your Relationship</Label>
                  <Input
                    id="relation_to_deceased"
                    value={formData.relation_to_deceased}
                    onChange={(e) => setFormData(prev => ({ ...prev, relation_to_deceased: e.target.value }))}
                    placeholder="e.g., Friend, Family, Colleague"
                  />
                </div>
                
                <div>
                  <Label htmlFor="email">Email (optional)</Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="your.email@example.com"
                  />
                </div>
                
                <div>
                  <Label htmlFor="message">Your Message *</Label>
                  <Textarea
                    id="message"
                    value={formData.message}
                    onChange={(e) => setFormData(prev => ({ ...prev, message: e.target.value }))}
                    placeholder="Share your memories, thoughts, or message of remembrance..."
                    rows={4}
                    required
                  />
                </div>
                
                <div className="flex gap-2 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowForm(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={submitting}
                    className="flex-1"
                  >
                    {submitting ? 'Submitting...' : 'Submit Tribute'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Tributes Grid */}
        {tributes.length === 0 ? (
          <div className="text-center py-12">
            <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No tributes yet</p>
            <p className="text-gray-400 mt-2">Be the first to share a message of remembrance</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {tributes.map((tribute) => (
              <Card key={tribute.id} className="group hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">
                          {tribute.author_name}
                        </h4>
                        {tribute.relation_to_deceased && (
                          <p className="text-sm text-gray-500">
                            {tribute.relation_to_deceased}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    {/* Candle button */}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleLightCandle(tribute.id)}
                      className={`transition-colors ${
                        tribute.candle_lit
                          ? 'bg-orange-100 border-orange-300 text-orange-600'
                          : 'hover:bg-orange-50'
                      }`}
                    >
                      <Flame className={`w-4 h-4 ${tribute.candle_lit ? 'fill-current' : ''}`} />
                    </Button>
                  </div>

                  {/* Message */}
                  <p className="text-gray-700 mb-4 leading-relaxed">
                    {tribute.message}
                  </p>

                  {/* Footer */}
                  <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <Calendar className="w-4 h-4" />
                      <span>{new Date(tribute.created_at).toLocaleDateString()}</span>
                    </div>
                    
                    {tribute.candle_lit && (
                      <div className="flex items-center gap-1 text-orange-600">
                        <Flame className="w-4 h-4 fill-current" />
                        <span className="text-sm">Candle lit</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Candle counter */}
        {tributes.length > 0 && (
          <div className="mt-12 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-50 rounded-full">
              <Flame className="w-5 h-5 text-orange-600" />
              <span className="text-orange-800 font-medium">
                {tributes.filter(t => t.candle_lit).length} candles lit
              </span>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

export default TributesWall;
