
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ExamForm } from "@/components/ExamForm";
import { ExamList } from "@/components/ExamList";
import { Navbar } from "@/components/Navbar";
import { Calendar, Plus, List } from "lucide-react";

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState("add");

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Sınav Yönetimi</h1>
          <p className="text-gray-600">Sınavlarınızı ekleyin ve planlamalarını görüntüleyin</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 lg:w-96">
            <TabsTrigger value="add" className="flex items-center gap-2">
              <Plus className="h-4 w-4" />
              Sınav Ekle
            </TabsTrigger>
            <TabsTrigger value="list" className="flex items-center gap-2">
              <List className="h-4 w-4" />
              Sınav Listesi
            </TabsTrigger>
          </TabsList>

          <TabsContent value="add">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Yeni Sınav Ekle
                </CardTitle>
                <CardDescription>
                  Sınav bilgilerini girin, sistem otomatik olarak en uygun zamanı planlayacak
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ExamForm />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="list">
            <Card>
              <CardHeader>
                <CardTitle>Sınav Listesi ve Planlama</CardTitle>
                <CardDescription>
                  Eklenen sınavlar ve planlanan zamanlar
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ExamList />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Dashboard;
