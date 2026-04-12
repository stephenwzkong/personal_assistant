import { useState, useEffect } from "react";
import { useSearchParams } from "react-router";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Activity, Briefcase, DollarSign, Users, Target, Home as HomeIcon } from "lucide-react";
import { WellnessTab } from "./domains/WellnessTab";
import { ProductivityTab } from "./domains/ProductivityTab";
import { FinanceTab } from "./domains/FinanceTab";
import { SocialTab } from "./domains/SocialTab";
import { GoalsTab } from "./domains/GoalsTab";
import { useChatContext } from "../../contexts/ChatContext";

function Breadcrumb({ domainNames, activeTab }: { domainNames: Record<string, string>; activeTab: string }) {
  return (
    <div className="flex items-center gap-2 mb-6 text-sm text-gray-500">
      <HomeIcon className="w-4 h-4" />
      <span>/</span>
      <span>Domains</span>
      <span>/</span>
      <span className="text-gray-900">{domainNames[activeTab] || "Wellness"}</span>
    </div>
  );
}

export function DomainsPage() {
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState("wellness");
  const { prefillChat } = useChatContext();

  useEffect(() => {
    const tabParam = searchParams.get("tab");
    if (tabParam) {
      setActiveTab(tabParam);
    }
  }, [searchParams]);

  const handleQuickAction = (prompt: string) => {
    prefillChat(prompt);
  };

  const domainNames: Record<string, string> = {
    wellness: "Wellness",
    productivity: "Productivity",
    finance: "Finance",
    social: "Social",
    goals: "Goals"
  };

  return (
    <div className="h-full overflow-auto">
      <div className="max-w-7xl mx-auto p-6 lg:p-8">
        <Breadcrumb domainNames={domainNames} activeTab={activeTab} />

        <div className="mb-8">
          <h1 className="text-3xl text-gray-900 mb-2">Life Domains</h1>
          <p className="text-gray-600">Track and manage different areas of your life</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-5 mb-8 h-auto gap-2">
            <TabsTrigger value="wellness" className="flex flex-col lg:flex-row items-center gap-2 py-3">
              <Activity className="w-4 h-4" />
              <span className="text-xs lg:text-sm">Wellness</span>
            </TabsTrigger>
            <TabsTrigger value="productivity" className="flex flex-col lg:flex-row items-center gap-2 py-3">
              <Briefcase className="w-4 h-4" />
              <span className="text-xs lg:text-sm">Productivity</span>
            </TabsTrigger>
            <TabsTrigger value="finance" className="flex flex-col lg:flex-row items-center gap-2 py-3">
              <DollarSign className="w-4 h-4" />
              <span className="text-xs lg:text-sm">Finance</span>
            </TabsTrigger>
            <TabsTrigger value="social" className="flex flex-col lg:flex-row items-center gap-2 py-3">
              <Users className="w-4 h-4" />
              <span className="text-xs lg:text-sm">Social</span>
            </TabsTrigger>
            <TabsTrigger value="goals" className="flex flex-col lg:flex-row items-center gap-2 py-3">
              <Target className="w-4 h-4" />
              <span className="text-xs lg:text-sm">Goals</span>
            </TabsTrigger>
          </TabsList>
          <TabsContent value="wellness"><WellnessTab onQuickAction={handleQuickAction} /></TabsContent>
          <TabsContent value="productivity"><ProductivityTab onQuickAction={handleQuickAction} /></TabsContent>
          <TabsContent value="finance"><FinanceTab onQuickAction={handleQuickAction} /></TabsContent>
          <TabsContent value="social"><SocialTab onQuickAction={handleQuickAction} /></TabsContent>
          <TabsContent value="goals"><GoalsTab onQuickAction={handleQuickAction} /></TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
