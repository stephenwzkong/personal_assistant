import { createBrowserRouter } from "react-router";
import { Root } from "./components/Root";
import { Home } from "./components/Home";
import { CalendarPage } from "./components/CalendarPage";
import { DomainsPage } from "./components/DomainsPage";
import { NotFound } from "./components/NotFound";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: Home },
      { path: "calendar", Component: CalendarPage },
      { path: "domains", Component: DomainsPage },
      { path: "*", Component: NotFound },
    ],
  },
]);