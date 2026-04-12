import { Outlet, Link, useLocation } from "react-router";
import { Calendar, LayoutDashboard, MessageCircle, ListTodo } from "lucide-react";
import { ChatProvider } from "../../contexts/ChatContext";

export function Root() {
  const location = useLocation();

  const isActive = (path: string) => {
    if (path === "/" && location.pathname === "/") return true;
    if (path !== "/" && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <ChatProvider>
      <div className="h-screen flex flex-col bg-white">
        {/* Top Navigation */}
        <header className="border-b border-gray-200 bg-white">
          <div className="flex items-center justify-between px-6 py-3">
            <div className="flex items-center gap-8">
              <Link to="/" className="text-lg text-gray-900 hover:text-gray-700 transition-colors">
                Life Coordination
              </Link>
              <nav className="flex items-center gap-1">
                <Link
                  to="/"
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    isActive("/") && location.pathname === "/"
                      ? "bg-gray-100 text-gray-900"
                      : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  <MessageCircle className="w-4 h-4" />
                  <span>Chat</span>
                </Link>
                <Link
                  to="/dashboard"
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    isActive("/dashboard")
                      ? "bg-gray-100 text-gray-900"
                      : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  <LayoutDashboard className="w-4 h-4" />
                  <span>Dashboard</span>
                </Link>
                <Link
                  to="/tasks"
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    isActive("/tasks")
                      ? "bg-gray-100 text-gray-900"
                      : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  <ListTodo className="w-4 h-4" />
                  <span>Tasks</span>
                </Link>
                <Link
                  to="/calendar"
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    isActive("/calendar")
                      ? "bg-gray-100 text-gray-900"
                      : "text-gray-500 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  <Calendar className="w-4 h-4" />
                  <span>Calendar</span>
                </Link>
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex-1 overflow-hidden">
          <Outlet />
        </main>
      </div>
    </ChatProvider>
  );
}
