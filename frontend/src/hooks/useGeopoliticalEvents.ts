import { useQuery } from '@tanstack/react-query';
import { geopoliticalEventsApi } from '../api/client';
import { format } from 'date-fns';

export const useGeopoliticalEvents = (date: Date) => {
  const dateStr = format(date, 'yyyy-MM-dd');

  return useQuery({
    queryKey: ['geopolitical-events', dateStr],
    queryFn: () => geopoliticalEventsApi.getEvents(dateStr),
    enabled: !!date,
    staleTime: 5 * 60 * 1000, // Data considered fresh for 5 minutes
    gcTime: 30 * 60 * 1000, // Cached data kept for 30 minutes
    refetchOnWindowFocus: false,
    refetchOnMount: false,
  });
};



