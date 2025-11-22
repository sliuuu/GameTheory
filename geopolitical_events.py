"""
Geopolitical Events Data Source
Provides market-moving geopolitical events for the dashboard
"""

from datetime import datetime, timedelta
from typing import List, Dict
import random
import urllib.parse


class GeopoliticalEventsSource:
    """
    Provides geopolitical events that move markets.
    In a production system, this would fetch from news APIs, RSS feeds, or databases.
    For now, we'll use a curated list of event types that can be matched to market conditions.
    """
    
    EVENT_TYPES = [
        {
            "type": "Trade Dispute",
            "impact": "high",
            "description_template": "{country1} and {country2} trade tensions escalate",
            "market_impact": "negative"
        },
        {
            "type": "Diplomatic Summit",
            "impact": "medium",
            "description_template": "{country1} and {country2} hold diplomatic talks",
            "market_impact": "positive"
        },
        {
            "type": "Military Exercise",
            "impact": "high",
            "description_template": "{country1} conducts military exercises near {country2}",
            "market_impact": "negative"
        },
        {
            "type": "Sanctions Announcement",
            "impact": "high",
            "description_template": "{country1} announces new sanctions against {country2}",
            "market_impact": "negative"
        },
        {
            "type": "Trade Agreement",
            "impact": "medium",
            "description_template": "{country1} and {country2} sign new trade agreement",
            "market_impact": "positive"
        },
        {
            "type": "Currency Intervention",
            "impact": "medium",
            "description_template": "{country1} central bank intervenes in currency markets",
            "market_impact": "mixed"
        },
        {
            "type": "Energy Dispute",
            "impact": "high",
            "description_template": "Energy supply tensions between {country1} and {country2}",
            "market_impact": "negative"
        },
        {
            "type": "Technology Export Restrictions",
            "impact": "high",
            "description_template": "{country1} restricts technology exports to {country2}",
            "market_impact": "negative"
        },
        {
            "type": "Alliance Strengthening",
            "impact": "medium",
            "description_template": "{country1} and {country2} strengthen military alliance",
            "market_impact": "positive"
        },
        {
            "type": "Territorial Dispute",
            "impact": "very_high",
            "description_template": "Tensions rise over territorial claims between {country1} and {country2}",
            "market_impact": "negative"
        }
    ]
    
    COUNTRIES = ["USA", "China", "Japan", "Germany", "Taiwan"]
    
    # Major news sources for geopolitical and financial news
    NEWS_SOURCES = [
        {"name": "Reuters", "url": "https://www.reuters.com/search/news?blob={query}"},
        {"name": "Bloomberg", "url": "https://www.bloomberg.com/search?query={query}"},
        {"name": "Financial Times", "url": "https://www.ft.com/search?q={query}"},
        {"name": "BBC News", "url": "https://www.bbc.com/search?q={query}"},
        {"name": "CNN", "url": "https://www.cnn.com/search?q={query}"},
    ]
    
    def __init__(self):
        self.events = []
    
    def _generate_news_sources(self, event_type: str, countries: List[str], title: str) -> List[Dict[str, str]]:
        """Generate news source links based on event type and countries"""
        # Create search query from event type and countries
        query_parts = [event_type]
        query_parts.extend(countries)
        query = " ".join(query_parts)
        query_encoded = urllib.parse.quote(query)
        
        # Generate links for top 3 news sources
        sources = []
        for source in self.NEWS_SOURCES[:3]:
            sources.append({
                "name": source["name"],
                "url": source["url"].format(query=query_encoded)
            })
        
        return sources
    
    def generate_events_from_market_data(self, market_data: Dict, date: datetime) -> List[Dict]:
        """
        Generate relevant geopolitical events based on market conditions.
        In production, this would analyze news feeds, but for now we'll infer from market movements.
        """
        events = []
        
        # Analyze market conditions to infer events
        vix = market_data.get("VIX", 0.0)
        gold = market_data.get("Gold", 0.0)
        usa_return = market_data.get("USA", 0.0) or market_data.get("SP500", 0.0)
        china_return = market_data.get("China", 0.0)
        taiwan_return = market_data.get("Taiwan", 0.0) or market_data.get("TAIEX", 0.0)
        japan_return = market_data.get("Japan", 0.0) or market_data.get("Nikkei225", 0.0)
        germany_return = market_data.get("Germany", 0.0) or market_data.get("DAX", 0.0)
        hang_seng = market_data.get("HangSeng", 0.0)
        
        # High VIX + rising gold = geopolitical tension
        if vix > 0.1 and gold > 0.02:
            event_data = {
                "date": date.strftime("%Y-%m-%d"),
                "type": "Territorial Dispute",
                "title": "Rising tensions in Asia-Pacific region",
                "description": "Increased volatility and safe-haven demand suggest heightened geopolitical tensions",
                "impact": "very_high",
                "countries": ["USA", "China", "Taiwan"],
                "market_impact": "negative",
                "relevance_score": 0.9
            }
            event_data["news_sources"] = self._generate_news_sources(
                event_data["type"], event_data["countries"], event_data["title"]
            )
            events.append(event_data)
        
        # Negative returns in both USA and China = trade tensions
        if usa_return < -0.02 and china_return < -0.02:
            event_data = {
                "date": date.strftime("%Y-%m-%d"),
                "type": "Trade Dispute",
                "title": "US-China trade tensions escalate",
                "description": "Synchronized market declines suggest ongoing trade friction",
                "impact": "high",
                "countries": ["USA", "China"],
                "market_impact": "negative",
                "relevance_score": 0.85
            }
            event_data["news_sources"] = self._generate_news_sources(
                event_data["type"], event_data["countries"], event_data["title"]
            )
            events.append(event_data)
        
        # High VIX alone = uncertainty
        if vix > 0.15:
            event_data = {
                "date": date.strftime("%Y-%m-%d"),
                "type": "Market Uncertainty",
                "title": "Elevated market volatility",
                "description": "High VIX indicates significant geopolitical or economic uncertainty",
                "impact": "high",
                "countries": ["USA"],
                "market_impact": "negative",
                "relevance_score": 0.75
            }
            event_data["news_sources"] = self._generate_news_sources(
                event_data["type"], event_data["countries"], event_data["title"]
            )
            events.append(event_data)
        
        # Strong gold rally = safe haven demand
        if gold > 0.03:
            event_data = {
                "date": date.strftime("%Y-%m-%d"),
                "type": "Safe Haven Demand",
                "title": "Investors seek safe havens",
                "description": "Strong gold rally indicates risk-off sentiment and geopolitical concerns",
                "impact": "medium",
                "countries": ["USA", "China"],
                "market_impact": "negative",
                "relevance_score": 0.7
            }
            event_data["news_sources"] = self._generate_news_sources(
                event_data["type"], event_data["countries"], event_data["title"]
            )
            events.append(event_data)
        
        # Currency movements = intervention or policy changes
        usdcny = market_data.get("USDCNY", 0.0)
        if abs(usdcny) > 0.01:
            event_data = {
                "date": date.strftime("%Y-%m-%d"),
                "type": "Currency Intervention",
                "title": "Significant USD/CNY movement",
                "description": f"USD/CNY moved {'up' if usdcny > 0 else 'down'} {abs(usdcny)*100:.2f}%, suggesting policy intervention or trade flow changes",
                "impact": "medium",
                "countries": ["USA", "China"],
                "market_impact": "mixed",
                "relevance_score": 0.65
            }
            event_data["news_sources"] = self._generate_news_sources(
                event_data["type"], event_data["countries"], event_data["title"]
            )
            events.append(event_data)
        
        # Taiwan underperformance = cross-strait tensions
        if taiwan_return < -0.03:
            event_data = {
                "date": date.strftime("%Y-%m-%d"),
                "type": "Cross-Strait Tensions",
                "title": "Taiwan market underperforms",
                "description": "Significant Taiwan market decline may indicate cross-strait geopolitical concerns",
                "impact": "high",
                "countries": ["China", "Taiwan", "USA"],
                "market_impact": "negative",
                "relevance_score": 0.8
            }
            event_data["news_sources"] = self._generate_news_sources(
                event_data["type"], event_data["countries"], event_data["title"]
            )
            events.append(event_data)
        
        # Always ensure we have at least some events based on general market conditions
        if len(events) < 3:
            # Add general market condition events
            avg_return = (usa_return + china_return + japan_return + germany_return + taiwan_return) / 5
            if avg_return < -0.01:
                event_data = {
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "Market Correction",
                    "title": "Broad market decline across major indices",
                    "description": f"Average return of {avg_return*100:.2f}% suggests global economic concerns or geopolitical uncertainty",
                    "impact": "medium",
                    "countries": ["USA", "China", "Japan", "Germany", "Taiwan"],
                    "market_impact": "negative",
                    "relevance_score": 0.6
                }
                event_data["news_sources"] = self._generate_news_sources(
                    event_data["type"], event_data["countries"], event_data["title"]
                )
                events.append(event_data)
            
            if abs(vix) > 0.05:
                event_data = {
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "Volatility Spike",
                    "title": f"VIX {'surged' if vix > 0 else 'declined'} {abs(vix)*100:.1f}%",
                    "description": f"Significant volatility movement indicates changing market sentiment and geopolitical risk perception",
                    "impact": "medium",
                    "countries": ["USA"],
                    "market_impact": "negative" if vix > 0 else "positive",
                    "relevance_score": 0.55
                }
                event_data["news_sources"] = self._generate_news_sources(
                    event_data["type"], event_data["countries"], event_data["title"]
                )
                events.append(event_data)
            
            # Lower thresholds for detecting market movements
            if abs(japan_return) > 0.005:  # 0.5% threshold
                event_data = {
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "Market Movement",
                    "title": f"Japan market {'declined' if japan_return < 0 else 'gained'} {abs(japan_return)*100:.2f}%",
                    "description": f"Significant movement in Japanese markets may reflect regional geopolitical developments or economic policy changes",
                    "impact": "medium",
                    "countries": ["Japan"],
                    "market_impact": "negative" if japan_return < 0 else "positive",
                    "relevance_score": 0.5
                }
                event_data["news_sources"] = self._generate_news_sources(
                    event_data["type"], event_data["countries"], event_data["title"]
                )
                events.append(event_data)
            
            if abs(china_return) > 0.005:  # 0.5% threshold
                event_data = {
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "Market Movement",
                    "title": f"China market {'declined' if china_return < 0 else 'gained'} {abs(china_return)*100:.2f}%",
                    "description": f"Movement in Chinese markets may indicate policy changes, trade developments, or regional tensions",
                    "impact": "medium",
                    "countries": ["China"],
                    "market_impact": "negative" if china_return < 0 else "positive",
                    "relevance_score": 0.5
                }
                event_data["news_sources"] = self._generate_news_sources(
                    event_data["type"], event_data["countries"], event_data["title"]
                )
                events.append(event_data)
        
        # If still no events, generate default events based on current market state
        if len(events) == 0:
            # Generate baseline events for monitoring
            event_data = {
                "date": date.strftime("%Y-%m-%d"),
                "type": "Market Monitoring",
                "title": "Ongoing monitoring of geopolitical developments",
                "description": "Markets are relatively stable. Monitoring key geopolitical indicators including trade relations, currency movements, and regional tensions.",
                "impact": "low",
                "countries": ["USA", "China", "Japan", "Germany", "Taiwan"],
                "market_impact": "mixed",
                "relevance_score": 0.4
            }
            event_data["news_sources"] = self._generate_news_sources(
                event_data["type"], event_data["countries"], event_data["title"]
            )
            events.append(event_data)
            
            # Add event based on any non-zero market movement
            if japan_return != 0.0:
                event_data = {
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "Regional Market Activity",
                    "title": f"Japan market movement: {japan_return*100:.2f}%",
                    "description": "Japanese market showing activity, potentially reflecting regional economic or geopolitical factors",
                    "impact": "low",
                    "countries": ["Japan"],
                    "market_impact": "negative" if japan_return < 0 else "positive",
                    "relevance_score": 0.35
                }
                event_data["news_sources"] = self._generate_news_sources(
                    event_data["type"], event_data["countries"], event_data["title"]
                )
                events.append(event_data)
            
            if taiwan_return != 0.0:
                event_data = {
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "Cross-Strait Monitoring",
                    "title": f"Taiwan market activity: {taiwan_return*100:.2f}%",
                    "description": "Taiwan market movement may reflect cross-strait relations or regional economic conditions",
                    "impact": "medium",
                    "countries": ["Taiwan", "China"],
                    "market_impact": "negative" if taiwan_return < 0 else "positive",
                    "relevance_score": 0.4
                }
                event_data["news_sources"] = self._generate_news_sources(
                    event_data["type"], event_data["countries"], event_data["title"]
                )
                events.append(event_data)
        
        # Sort by relevance score and return top 5
        events.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return events[:5]
    
    def get_events(self, market_data: Dict, date: datetime) -> List[Dict]:
        """Get top 5 market-moving geopolitical events"""
        return self.generate_events_from_market_data(market_data, date)

