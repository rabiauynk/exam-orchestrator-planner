
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Calendar, Clock, MapPin, Users, Computer } from "lucide-react";

// Örnek planlama verisi
const schedule = [
  {
    date: "15/01/2024",
    timeSlots: [
      {
        time: "09:00-11:00",
        room: "BM-201",
        exam: {
          course: "Veri Yapıları",
          department: "Bilgisayar Müh.",
          students: 45,
          needsComputer: true
        }
      },
      {
        time: "14:00-15:30",
        room: "BM-101",
        exam: {
          course: "Matematik I",
          department: "Endüstri Müh.",
          students: 60,
          needsComputer: false
        }
      }
    ]
  },
  {
    date: "16/01/2024",
    timeSlots: [
      {
        time: "10:00-12:30",
        room: "BM-Lab1",
        exam: {
          course: "Yazılım Mühendisliği",
          department: "Bilgisayar Müh.",
          students: 35,
          needsComputer: true
        }
      },
      {
        time: "15:00-16:30",
        room: "BM-102",
        exam: {
          course: "Fizik I",
          department: "Elektrik-Elektronik Müh.",
          students: 50,
          needsComputer: false
        }
      }
    ]
  }
];

export const ExamSchedule = () => {
  return (
    <div className="space-y-6">
      {schedule.map((day, dayIndex) => (
        <Card key={dayIndex}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              {day.date}
            </CardTitle>
            <CardDescription>
              {day.timeSlots.length} sınav planlanmış
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {day.timeSlots.map((slot, slotIndex) => (
                <div key={slotIndex} className="border rounded-lg p-4 bg-gray-50">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1 text-sm font-medium">
                          <Clock className="h-4 w-4" />
                          {slot.time}
                        </div>
                        <div className="flex items-center gap-1 text-sm">
                          <MapPin className="h-4 w-4" />
                          {slot.room}
                        </div>
                      </div>
                      
                      <h4 className="font-semibold text-lg">{slot.exam.course}</h4>
                      <p className="text-gray-600">{slot.exam.department}</p>
                      
                      <div className="flex items-center gap-4 text-sm">
                        <div className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          {slot.exam.students} öğrenci
                        </div>
                        {slot.exam.needsComputer && (
                          <Badge variant="secondary" className="flex items-center gap-1">
                            <Computer className="h-3 w-3" />
                            Bilgisayar
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ))}
      
      {schedule.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Henüz planlanmış sınav bulunmamaktadır.
        </div>
      )}
    </div>
  );
};
