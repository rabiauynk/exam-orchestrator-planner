
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { format } from "date-fns";
import { CalendarIcon, Save } from "lucide-react";
import { cn } from "@/lib/utils";

export const ExamWeekSettings = () => {
  const [startDate, setStartDate] = useState<Date>();
  const [endDate, setEndDate] = useState<Date>();

  const handleSave = () => {
    if (!startDate || !endDate) {
      alert("Lütfen başlangıç ve bitiş tarihlerini seçin!");
      return;
    }

    if (startDate >= endDate) {
      alert("Başlangıç tarihi bitiş tarihinden önce olmalıdır!");
      return;
    }

    console.log("Sınav haftası aralığı:", { startDate, endDate });
    alert("Sınav haftası aralığı başarıyla kaydedildi!");
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-2">Sınav Haftası Aralığı</h3>
        <p className="text-gray-600">Sınavların yapılabileceği tarih aralığını belirleyin</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label>Başlangıç Tarihi</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-full justify-start text-left font-normal",
                  !startDate && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {startDate ? format(startDate, "dd/MM/yyyy") : "Başlangıç tarihi seçin"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={startDate}
                onSelect={setStartDate}
                disabled={(date) => date < new Date()}
                initialFocus
                className="pointer-events-auto"
              />
            </PopoverContent>
          </Popover>
        </div>

        <div className="space-y-2">
          <Label>Bitiş Tarihi</Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  "w-full justify-start text-left font-normal",
                  !endDate && "text-muted-foreground"
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {endDate ? format(endDate, "dd/MM/yyyy") : "Bitiş tarihi seçin"}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={endDate}
                onSelect={setEndDate}
                disabled={(date) => date < new Date() || (startDate && date <= startDate)}
                initialFocus
                className="pointer-events-auto"
              />
            </PopoverContent>
          </Popover>
        </div>
      </div>

      {startDate && endDate && (
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-blue-800">
            <strong>Seçilen Aralık:</strong> {format(startDate, "dd/MM/yyyy")} - {format(endDate, "dd/MM/yyyy")}
          </p>
          <p className="text-sm text-blue-600 mt-1">
            Bu tarihler arasında kullanıcılar sınav tarihi tercihlerini yapabilecekler.
          </p>
        </div>
      )}

      <Button onClick={handleSave} className="w-full">
        <Save className="mr-2 h-4 w-4" />
        Aralığı Kaydet
      </Button>
    </div>
  );
};
