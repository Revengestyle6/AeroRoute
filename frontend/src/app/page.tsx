"use client";

import React, { useEffect, useState } from "react";

type Airport = {
  airport: string;
  lat: number;
  lng: number;
  geocode?: string;
};

export default function AirportMap(): JSX.Element {
  const [airports, setAirports] = useState<Airport[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAirports = async () => {
      try {
          const response = await fetch('http://localhost:5001/api/airports/all');
        if (!response.ok) throw new Error('Failed to fetch airports');
        const result = await response.json();
        
        // Transform data for Recharts scatter chart
        const chartData: Airport[] = result.airports.map((airport: any) => ({
          lat: Number(airport.lat),
          lng: Number(airport.lng),
          airport: String(airport.airport),
          geocode: airport.geocode,
        }));
        
        setAirports(chartData);
        setLoading(false);
      } catch (err: any) {
        setError(err?.message ? String(err.message) : String(err));
        setLoading(false);
      }
    };

    fetchAirports();
  }, []);

  if (loading) return <div className="p-4">Loading airport data...</div>;
  if (error) return <div className="p-4 text-red-600">Error: {error}</div>;

  return (
    <div className="w-full h-screen flex flex-col">
      <div className="p-4 bg-gray-100">
        <h1 className="text-2xl font-bold">US Flight Route Airports</h1>
        <p className="text-gray-600">{airports.length} airports plotted by latitude/longitude</p>
      </div>
      <div className="flex-1">
        <div className="w-full h-full">
          <iframe
            src="http://localhost:5001/api/map"
            title="US Flight Routes Map"
            style={{ width: '100%', height: '100%', border: 0 }}
          />
        </div>
      </div>
    </div>
  );
}
