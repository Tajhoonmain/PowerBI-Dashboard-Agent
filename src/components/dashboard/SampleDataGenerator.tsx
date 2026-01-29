import { Button } from '@/components/ui/button';
import { Download } from 'lucide-react';

export function SampleDataGenerator() {
  const generateSampleCSV = () => {
    const months = ['January', 'February', 'March', 'April', 'May', 'June'];
    const regions = ['North', 'South', 'East', 'West'];
    
    const rows = [];
    
    regions.forEach(region => {
      months.forEach((month, idx) => {
        rows.push({
          Region: region,
          Month: month,
          Revenue: Math.floor(Math.random() * 50000) + 10000,
          Orders: Math.floor(Math.random() * 500) + 50,
          Customers: Math.floor(Math.random() * 300) + 30,
        });
      });
    });

    const csv = [
      'Region,Month,Revenue,Orders,Customers',
      ...rows.map(row => `${row.Region},${row.Month},${row.Revenue},${row.Orders},${row.Customers}`)
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample-data.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="mt-6 text-center">
      <p className="text-sm text-white/40 mb-3">Don't have data? Try our sample dataset:</p>
      <Button
        onClick={generateSampleCSV}
        variant="outline"
        className="border-white/20 hover:border-[#00d9ff]/50 hover:bg-[#00d9ff]/10"
      >
        <Download className="w-4 h-4 mr-2" />
        Download Sample CSV
      </Button>
    </div>
  );
}
