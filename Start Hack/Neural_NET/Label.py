class LabelDataset:
    def __init__(self, data, mean_delta):
        self.data = data
        self.mean_delta = mean_delta
        
    def label_classify(self):
        label_data = []
     
        for i in range(len(self.data)-1):

            if abs(self.data[i+1] - self.data[i]) > self.mean_delta/20:
                label_data.append([1])  # 1 is label for big diff
            else:
                label_data.append([0])  # 0 is label for no diff
       
        label_data = [j for j in label_data]
        return label_data
    
    def up_or_down(self):
        up_down = []
        for i in range(len(self.data)-1):
            if self.data[i+1] - self.data[i] > self.mean_delta/13:
                up_down.append(1)
            else:
                up_down.append(0)
        up_down = up_down[-168:]
        if up_down.count(1) > up_down.count(0):
            return "up", up_down.count(1), up_down.count(0)
        else:
            return "down", up_down.count(1), up_down.count(0)
    


    