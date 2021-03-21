import torch
from torch import optim, nn
from Classifier import Classifier_
from Data import label_array, status_info
from get_feature import feature_array
from torch.utils.data import DataLoader, TensorDataset, random_split
from Label import LabelDataset

features = torch.from_numpy(feature_array).type(torch.float)
targets = torch.from_numpy(label_array).type(torch.float)


#print(features.size())
#print(targets.size())

dataset = TensorDataset(features, targets)
data_loader = DataLoader(dataset, batch_size=64)


def neural_N(epochs, learning_rate, data_loader, model):
    model = model
    criterion = nn.NLLLoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)  # Adam or SGD
    epochs = epochs
    pred_lst = []
    for e in range(epochs):
        running_loss = 0
        for features, targets in data_loader:
            optimizer.zero_grad()
            output = model(features)
            loss = criterion(output, torch.max(targets,1)[1])
            pred_lst.append(output)
            ps = torch.exp(output)
            top_p, top_class = ps.topk(1, dim=1)

            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        else:
            print(f"Training loss : {running_loss/len(data_loader)}")
            #print(pred_lst[-1])
    return pred_lst
        
        
#print(neural_N(10, 0.01, data_loader, Classifier_()))

def predict(data_loader, model, status):
    pred_lst = neural_N(20,0.01,data_loader,model)
    mean_val = 0
    
    for i in pred_lst:
        for j in i:
            for k in j.tolist():
                mean_val += k
    mean_val = mean_val * 1.6 / 2725
 
    
    evalu = 0
    for n in range(1,40):
        for k in pred_lst[-1][-n].tolist():
            evalu += k
        for k in pred_lst[-2][-n].tolist():
            evalu += k
        for k in pred_lst[-3][-n].tolist():
            evalu += k
        for k in pred_lst[-4][-n].tolist():
            evalu += k
    
    
    #print(evalu, mean_val)

    if abs(evalu) - abs(mean_val) > abs(mean_val) * 0.15:
        return True, status
    else:
        return False, status




