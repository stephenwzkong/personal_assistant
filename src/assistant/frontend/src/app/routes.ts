import { createBrowserRouter } from "react-router";
import { Root } from "./components/Root";
import { ChatPage } from "./components/ChatPage";
import { DashboardPage } from "./components/DashboardPage";
import { CalendarPage } from "./components/CalendarPage";
import { TasksPage } from "./components/TasksPage";
import { NotFound } from "./components/NotFound";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      { index: true, Component: ChatPage },
      { path: "dashboard", Component: DashboardPage },
      { path: "calendar", Component: CalendarPage },
      { path: "tasks", Component: TasksPage },
      { path: "*", Component: NotFound },
    ],
  },
]);
