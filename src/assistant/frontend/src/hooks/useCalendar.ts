import { useState, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { getCalendarGrid, getCalendarEvents } from "../lib/api";
import type { CalendarGridResponse, CalendarEventsResponse } from "../lib/api";

function getMonday(d?: Date): string {
  const ref = d ?? new Date();
  const day = ref.getDay();
  const diff = ref.getDate() - day + (day === 0 ? -6 : 1);
  const monday = new Date(ref.setDate(diff));
  return monday.toISOString().slice(0, 10);
}

export function useCalendarGrid() {
  const [weekStart, setWeekStart] = useState<string>(getMonday);

  const query = useQuery<CalendarGridResponse>({
    queryKey: ["calendarGrid", weekStart],
    queryFn: () => getCalendarGrid(weekStart),
  });

  const navigateWeek = useCallback((direction: number) => {
    setWeekStart((prev) => {
      const d = new Date(prev);
      d.setDate(d.getDate() + 7 * direction);
      return d.toISOString().slice(0, 10);
    });
  }, []);

  const goToToday = useCallback(() => {
    setWeekStart(getMonday());
  }, []);

  return {
    ...query,
    weekStart,
    navigateWeek,
    goToToday,
  };
}

export function useCalendarEvents(startDate?: string, endDate?: string) {
  return useQuery<CalendarEventsResponse>({
    queryKey: ["calendarEvents", startDate, endDate],
    queryFn: () => getCalendarEvents(startDate, endDate),
    enabled: !!startDate,
  });
}
